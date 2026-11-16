"""Entry point: builds the GJH Chibi Visitor from scratch and runs every gate.

  Blender --background --factory-startup --python-exit-code 1 \
      --python models/gjh-chibi-visitor-code/src/build.py -- --out models/gjh-chibi-visitor-code [--keep-going] [--no-renders]

Writes exports/, sources/, previews/, textures/ and qa/run-001/report.json.
Exits non-zero when any gate fails (with --keep-going all stages still run).
"""
import hashlib
import json
import os
import sys
import time

sys.dont_write_bytecode = True        # keep __pycache__ out of the model folder
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "qa"))

import bpy  # noqa: E402

import anim  # noqa: E402
import assemble  # noqa: E402
import checks  # noqa: E402
import config as C  # noqa: E402
import export  # noqa: E402
import reference  # noqa: E402
import render  # noqa: E402
import rig as R  # noqa: E402
import silhouette  # noqa: E402
from head import EXPRESSIONS  # noqa: E402

GAITS = {"Walk": (32, 0.20, 0.56), "Run": (20, 0.30, 0.40)}
CLIP_NAMES = ["Idle", "Walk", "Run", "Sit", "Wave", "Talk", "ShopBrowse", "PickUp", "Inspect", "Point", "Nod",
              "Cheer"]
OVERLAP_MUST_BE_ZERO = [("Face", "Hair"), ("Backpack", "Tee"), ("Backpack", "Body"), ("Shoes", "Body"),
                        ("Hair", "Tee"), ("Watch", "Tee")]
OVERLAP_ALLOWED = [("Body", "Tee"), ("Body", "Hair"), ("Body", "Watch"), ("Jeans", "Tee"), ("Jeans", "Shoes")]


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[argv.index("--out") + 1] if "--out" in argv else os.path.dirname(HERE)
    return os.path.abspath(out), "--keep-going" in argv, "--no-renders" in argv


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def gate(stage, name, items):
    return {"stage": stage, "name": name, "checks": items, "pass": all(i["pass"] for i in items)}


def main():
    out, keep_going, no_renders = args()
    started = time.time()
    qa_dir = os.path.join(out, "qa", "run-001")
    previews = os.path.join(out, "previews")
    for d in (qa_dir, previews, os.path.join(out, "exports"), os.path.join(out, "sources")):
        os.makedirs(d, exist_ok=True)
    bpy.context.scene.render.fps = 30
    report = {"asset": C.ASSET_ID, "blender": bpy.app.version_string, "gates": []}

    def finish(code):
        report["seconds"] = round(time.time() - started, 1)
        report["pass"] = all(g["pass"] for g in report["gates"])
        with open(os.path.join(qa_dir, "report.json"), "w") as handle:
            json.dump(report, handle, indent=2)
        print("REPORT", json.dumps({g["name"]: g["pass"] for g in report["gates"]}))
        if code or not report["pass"]:
            sys.exit(1)

    def record(g):
        report["gates"].append(g)
        print("GATE", g["stage"], g["name"], "PASS" if g["pass"] else "FAIL")
        if not g["pass"] and not keep_going:
            finish(1)

    # Stage 0 - reference masks.
    ref = reference.build(out)
    record(gate(0, "reference", reference.gate(ref)["checks"]))

    # Stages 1-5 - geometry.
    objects, built = assemble.build(out)
    m = checks.measure(objects)
    report["measure"] = m
    sil = silhouette.compare(out, qa_dir)
    report["silhouette"] = {v: r["rows"] for v, r in sil["views"].items()}
    body_iou = min(r["rows"]["body"]["iou"] for r in sil["views"].values())
    record(gate(1, "proportions", [
        checks.check("height (m)", m["height_m"], f"{C.HEIGHT} +/- {C.LANDMARK_TOLERANCE}",
                     abs(m["height_m"] - C.HEIGHT) <= C.LANDMARK_TOLERANCE),
        checks.check("feet on ground (m)", m["lowest_z_m"], "|z| <= 0.002", abs(m["lowest_z_m"]) <= 0.002),
        checks.check("body silhouette IoU (worst view)", body_iou, f">= {C.BLOCKOUT_IOU_MIN}",
                     body_iou >= C.BLOCKOUT_IOU_MIN),
    ]))
    ov = checks.overlaps(objects, OVERLAP_MUST_BE_ZERO + OVERLAP_ALLOWED)
    report["overlaps"] = ov
    record(gate(2, "body-and-clothes", [
        checks.check("triangles", m["triangles"], f"{C.TRI_BUDGET_MIN}-{C.TRI_BUDGET_MAX}",
                     C.TRI_BUDGET_MIN <= m["triangles"] <= C.TRI_BUDGET_MAX),
        checks.check("draw calls", m["draw_calls"], f"<= {C.DRAW_CALL_MAX}", m["draw_calls"] <= C.DRAW_CALL_MAX),
        checks.check("body silhouette IoU (worst view)", body_iou, f">= {C.BODY_IOU_MIN}", body_iou >= C.BODY_IOU_MIN),
        checks.check("inside-out parts", built["inside_out"], "[]", not built["inside_out"]),
    ] + [checks.check(f"overlap {a}|{b}", ov[f"{a}|{b}"], "0", ov[f"{a}|{b}"] == 0)
         for a, b in OVERLAP_MUST_BE_ZERO if (a, b) != ("Backpack", "Tee")]))   # that pair is stage 5
    keys = objects["Face"].data.shape_keys.key_blocks
    moved = {}
    for name in EXPRESSIONS:
        delta = max((keys[name].data[i].co - keys["Basis"].data[i].co).length for i in range(len(keys["Basis"].data)))
        moved[name] = round(delta, 4)
    clearance = checks.decal_clearance(objects["Face"], objects["Body"])
    report["decal_clearance"] = clearance
    record(gate(3, "face", [
        checks.check("expression keys", sorted(moved), sorted(EXPRESSIONS), sorted(moved) == sorted(EXPRESSIONS)),
        checks.check("decal triangles crossing the skin, per expression", clearance, "all 0",
                     all(v == 0 for v in clearance.values())),
    ] + [checks.check(f"key {k} moves the face (m)", v, "> 0.002", v > 0.002) for k, v in moved.items()]))
    hair_checks = []
    for view, r in sil["views"].items():
        head = r["rows"]["head"]
        hair_checks.append(checks.check(f"{view} head mean (px)", head["mean_px"], f"<= {C.SILHOUETTE_MEAN_MAX_PX}",
                                        head["mean_px"] <= C.SILHOUETTE_MEAN_MAX_PX))
        hair_checks.append(checks.check(f"{view} head max (px)", head["max_px"], f"<= {C.SILHOUETTE_MAX_PX}",
                                        head["max_px"] <= C.SILHOUETTE_MAX_PX))
    record(gate(4, "hair-silhouette", hair_checks))
    record(gate(5, "props", [checks.check("overlap Backpack|Tee", ov["Backpack|Tee"], "0", ov["Backpack|Tee"] == 0)]))

    # Stage 6 - rig and skin.
    collection = objects["Body"].users_collection[0]
    rig = R.build_armature(collection)
    for obj in objects.values():
        R.skin(obj, rig)
    ws = checks.weight_stats(objects)
    report["weights"] = ws
    bones = [b.name for b in rig.data.bones]
    deform_bones = [b.name for b in rig.data.bones if b.use_deform]

    # Stage 7 - animation.
    animator = anim.build_clips(rig, objects["Face"])
    export.rest_pose(rig, objects["Face"])
    deform = checks.deformation(objects, rig, animator.clips)
    report["deformation"] = deform
    record(gate(6, "rig-and-skin", [
        checks.check("deform bones", len(deform_bones), "20", len(deform_bones) == 20),
        checks.check("socket bones", sorted(set(bones) - set(deform_bones)), sorted(R.SOCKETS),
                     sorted(set(bones) - set(deform_bones)) == sorted(R.SOCKETS)),
        checks.check("unweighted vertices", ws["unweighted"], "0", ws["unweighted"] == 0),
        checks.check("vertices with > 4 influences", ws["over_four_influences"], "0", ws["over_four_influences"] == 0),
        checks.check("collapsed or stretched triangles in clips", deform["bad_triangles_total"], "0",
                     deform["bad_triangles_total"] == 0),
    ]))
    mo = checks.motion(objects, rig, animator.clips, GAITS)
    report["motion"] = mo
    clear = checks.clip_clearance(objects, rig, animator.clips)
    report["clip_clearance"] = clear
    record(gate(7, "animation", [
        checks.check("clips", [n for n, _ in animator.clips], CLIP_NAMES, [n for n, _ in animator.clips] == CLIP_NAMES),
        checks.check("loop seams (m)", mo["loops"], "<= 0.0005", all(v <= 0.0005 for v in mo["loops"].values())),
        checks.check("lowest shoe point per clip (m)", mo["lowest_shoe_z"], ">= -0.005",
                     all(v >= -0.005 for v in mo["lowest_shoe_z"].values())),
        checks.check("lowest point of any part per clip (m)", mo["lowest_any_z"], ">= -0.005",
                     all(v >= -0.005 for v in mo["lowest_any_z"].values())),
        checks.check("stance ankle off the ideal track (m)", mo["stance_error_m"], "<= 0.003",
                     all(v <= 0.003 for v in mo["stance_error_m"].values())),
    ] + [
        checks.check(f"extra {name} overlaps in clips (count, frame)", per_clip, "none",
                     not per_clip) for name, per_clip in clear["extra"].items()
    ]))

    # Stage 8 - export and previews.
    glb = export.export_glb(os.path.join(out, "exports", f"{C.ASSET_ID}.glb"), objects, rig)
    report["glb"] = {"path": os.path.relpath(glb, out), "bytes": os.path.getsize(glb), "sha256": sha256(glb)}
    if not no_renders:
        export.rest_pose(rig, objects["Face"])
        export.thumbnail(os.path.join(previews, "thumbnail.png"))
        export.turntable(previews)
        export.expression_shots(previews, objects["Face"])
        export.clip_shots(previews, rig, objects["Face"], animator.clips)
        render.preview_views(previews, prefix="ortho")
        export.rest_pose(rig, objects["Face"])
    blend = export.save_blend(os.path.join(out, "sources", f"{C.ASSET_ID}.blend"))
    report["source"] = {"path": os.path.relpath(blend, out), "sha256": sha256(blend)}
    record(gate(8, "export", [
        checks.check("GLB written (bytes)", report["glb"]["bytes"], "> 0 and < 4 MB",
                     0 < report["glb"]["bytes"] < 4_000_000),
    ]))
    finish(0)


main()
