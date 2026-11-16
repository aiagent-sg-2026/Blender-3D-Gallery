#!/usr/bin/env python3
"""Build, replay and inspect the visitor, or export an edited native master."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
AUTHOR=HERE/"authoring"
QA=HERE/"qa"
PREVIEW=HERE/"preview"

def run(command):
    subprocess.run([str(v) for v in command],check=True,cwd=ROOT,
                   env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def sources():
    entries=[HERE/"README.md",HERE/"build.py",HERE/".gitignore"]
    modules="accessories atlas blockout config fringe guides hair hair_bake hair_temple_fit swept_locks head meshkit motion scene skull_profile studio wardrobe".split()
    entries.extend(AUTHOR/(module+".py") for module in modules)
    entries.extend(AUTHOR/name for name in ("hair-sculpt.npz","hair-measurements.npz","hair-lock-mattes.npz"))
    calibration=AUTHOR/"hair-pigment-fit.npz"
    if calibration.exists():entries.append(calibration)
    for group in (PREVIEW,QA):
        entries.extend(sorted(entry for entry in group.iterdir() if entry.is_file() and not entry.name.startswith(".")))
    return entries

def package(stage,inputs):
    archive=stage/"visitor-kit.zip"
    files=[(f,f.relative_to(ROOT)) for f in inputs]
    files.extend((ROOT/name,Path(name)) for name in ("package.json","package-lock.json"))
    files.extend((f,HERE.relative_to(ROOT)/"delivery"/f.relative_to(stage)) for f in sorted(stage.rglob("*")) if f.is_file())
    with zipfile.ZipFile(archive,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
        for file,name in files:bundle.write(file,str(name))
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:raise IOError("Archive checksum failure")
        for file,name in files:
            if hashlib.sha256(bundle.read(str(name))).hexdigest()!=sha(file):raise IOError(str(name))

def blender_script(exe,script,args,master=None):
    command=[exe,"--background","--factory-startup","--disable-autoexec"]
    if master:command.append(master)
    run([*command,"--python-exit-code","1","--python",script,"--",*args])

def destination(explicit):
    if explicit:
        path=explicit.resolve()
    elif not (HERE/"delivery").exists():
        path=HERE/"delivery"
    else:
        stamp=dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
        path=HERE/"builds"/stamp
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Choose a new output directory to preserve the saved master: {path}")
    path.parent.mkdir(parents=True,exist_ok=True)
    return path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    fallback=shutil.which("blender") or "/Applications/Blender.app/Contents/MacOS/Blender"
    p.add_argument("--blender",default=fallback);p.add_argument("--reference",type=Path)
    p.add_argument("--output",type=Path,help="New directory; subsequent default builds go under builds/.")
    p.add_argument("--compare-before",type=Path,help="Preserved earlier delivery with bound captures; used with --all.")
    modes=p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--all",action="store_true");modes.add_argument("--export-only",type=Path,metavar="MASTER")
    modes.add_argument("--from-master",type=Path,metavar="MASTER",help="Assemble the saved character collections in a new scene.")
    args=p.parse_args()
    if args.compare_before and not args.all:p.error("--compare-before needs --all")
    if args.all:
        if not args.reference or not args.reference.is_file():p.error("--all needs the supplied PNG via --reference")
        header=args.reference.read_bytes()[:24]
        if header[:8]!=b"\x89PNG\r\n\x1a\n" or header[16:24]!=bytes.fromhex("0000060000000400"):
            p.error("The landmark overlay requires the original 1536 × 1024 character sheet")
    exe=args.blender
    dest=destination(args.output)
    build_inputs=sources() if args.all else []
    input_hashes={str(f.relative_to(HERE)):sha(f) for f in build_inputs}
    stage=Path(tempfile.mkdtemp(prefix=".visitor-stage-",dir=dest.parent))
    print(f"Building in {stage}",flush=True)
    try:
        if args.all:
            cp=stage/"checkpoints";(stage/"qa").mkdir()
            blender_script(exe,AUTHOR/"blockout.py",[cp])
            blender_script(exe,AUTHOR/"scene.py",["--out",stage,"--checkpoints"])
            with tempfile.TemporaryDirectory(prefix="visitor-replay-") as tmp:
                replay=Path(tmp)
                regen,assembly,saved=[replay/name for name in ("procedural-rebuild","collection-reassembly","master-export")]
                blender_script(exe,AUTHOR/"scene.py",["--out",regen])
                blender_script(exe,AUTHOR/"scene.py",["--out",assembly,"--assemble",stage/"visitor.blend"])
                blender_script(exe,AUTHOR/"scene.py",["--out",saved,"--export-only"],stage/"visitor.blend")
                edited=replay/"edited-guide"
                blender_script(exe,QA/"edit-guide.py",[edited],stage/"visitor.blend")
                run(["node",QA/"verify.mjs",stage,regen/"visitor.glb",assembly/"visitor.glb",saved/"visitor.glb",edited/"visitor.glb"])
                run(["node",PREVIEW/"bundle.mjs",stage/"visitor.glb",stage/"preview.html"])
                run(["node",PREVIEW/"bundle.mjs",cp/"01-blockout.glb",replay/"blockout.html"])
                run(["node",QA/"render.mjs",stage,args.reference.resolve(),replay/"blockout.html","--play-all"])
            run(["node",QA/"face-closure.mjs",stage])
            run(["node",QA/"hair-study.mjs",stage,args.reference.resolve()])
            run(["node",QA/"hair-register.mjs",stage,args.reference.resolve()])
            if args.compare_before:
                run(["node",QA/"compare.mjs",args.compare_before.resolve(),stage,args.reference.resolve()])
                with tempfile.TemporaryDirectory(prefix="visitor-original-") as baseline:
                    old=Path(baseline)
                    for name in ("visitor.glb","preview.html"):
                        shutil.copy2(args.compare_before/name,old/name)
                    run(["node",QA/"hair-register.mjs",old,args.reference.resolve()])
                    run(["node",QA/"compare-hair.mjs",old,stage,args.reference.resolve()])
            for source,name in ((stage/"visitor.glb","studio-portrait"),(stage/"visitor.blend","source-portrait")):
                blender_script(exe,QA/"portrait.py",[source,stage/"qa"/(name+".png")])
            blender_script(exe,QA/"native.py",[stage],stage/"visitor.blend")
            checks={n:json.loads((stage/"qa"/(n+".json")).read_text())["pass"] for n in ("native","geometry","runtime","face-closure")}
            if not all(checks.values()):raise RuntimeError(str(checks))
            report={"blender":subprocess.check_output([exe,"--version"],text=True).splitlines()[0],
                    "command":"python3 models/chibi-mall-visitor-modular/build.py --blender <Blender 5.1.2> --reference <supplied PNG> --all",
                    "reference":{"filename":args.reference.name,"sha256":sha(args.reference)},
                    "sources":input_hashes,
                    "checks":checks,"visualReview":"PENDING_INDEPENDENT_REVIEW",
                    "ownerReview":"PENDING",
                    "files":{str(f.relative_to(stage)):sha(f) for f in sorted(stage.rglob("*")) if f.is_file()}}
            (stage/"qa/build.json").write_text(json.dumps(report,indent=2)+"\n")
            package(stage,build_inputs)
            if input_hashes!={str(f.relative_to(HERE)):sha(f) for f in sources()}:
                raise RuntimeError("Model inputs changed during construction. Rebuild the saved revision into a new directory.")
        else:
            master=(args.export_only or args.from_master).resolve(strict=True)
            if args.from_master:blender_script(exe,AUTHOR/"scene.py",["--out",stage,"--assemble",master])
            else:blender_script(exe,AUTHOR/"scene.py",["--out",stage,"--export-only"],master)
            run(["node",QA/"verify.mjs",stage])
            run(["node",PREVIEW/"bundle.mjs",stage/"visitor.glb",stage/"preview.html"])
        # Keep existing artist edits. A finished build only appears at its destination after the gate.
        if dest.exists():raise FileExistsError(dest)
        stage.rename(dest)
    except Exception:
        print(f"Build stopped. Diagnostic outputs are in {stage}",flush=True)
        raise
    print(f"Built for visual review: {dest}",flush=True)

if __name__=="__main__":main()

