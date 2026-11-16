"""Optional remeasurement of four supplied views, locally, with pinned public weights."""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
from diffusers import MarigoldNormalsPipeline

DEPTH=("depth-anything/Depth-Anything-V2-Small-hf","5426e4f0f36572d16453bbda7a8389317b1bef99")
NORMAL=("prs-eth/marigold-normals-v1-1","09cfdd258cb281fa006cf1afcd2284376d16687d")
REGIONS={"front":(273,507),"profile":(748,979),"back":(969,1180),"quarter":(36,260)}


def measure(reference,device):
    sheet=Image.open(reference).convert("RGB")
    images={}
    for name,(left,right) in REGIONS.items():
        crop=sheet.crop((left,48,right,254))
        image=Image.new("RGB",(crop.width+48,crop.height+56),(235,233,245))
        image.paste(crop,(24,24))
        images[name]=image
    result={}
    model_id,revision=DEPTH
    processor=AutoImageProcessor.from_pretrained(model_id,revision=revision)
    estimator=AutoModelForDepthEstimation.from_pretrained(model_id,revision=revision,use_safetensors=True).to(device).eval()
    for name,image in images.items():
        inputs=processor(images=image,return_tensors="pt").to(device)
        with torch.inference_mode():depth=estimator(**inputs).predicted_depth
        depth=torch.nn.functional.interpolate(depth[:,None].cpu(),(image.height,image.width),mode="bicubic",align_corners=False)[0,0]
        result[name+"_depth"]=depth.numpy()[24:-32,24:-24].copy()
    del estimator
    if device=="mps":torch.mps.empty_cache()
    model_id,revision=NORMAL
    pipeline=MarigoldNormalsPipeline.from_pretrained(model_id,revision=revision,variant="fp16",torch_dtype=torch.float16,use_safetensors=True).to(device)
    pipeline.set_progress_bar_config(disable=True)
    for name,image in images.items():
        torch.manual_seed(19)
        normal=pipeline(image,num_inference_steps=5,processing_resolution=512,ensemble_size=1,output_type="np",generator=torch.Generator(device="cpu").manual_seed(19))
        result[name+"_normal"]=normal.prediction[0][24:-32,24:-24].copy()
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference",type=Path)
    parser.add_argument("destination",type=Path)
    parser.add_argument("--head",type=Path,required=True,help="Reference-aligned character GLB providing physical face and ears.")
    parser.add_argument("--device",default="mps" if torch.backends.mps.is_available() else "cpu")
    args=parser.parse_args()
    from hair_occlusion import read_face
    data=measure(args.reference,args.device)
    data["skin_xyz"],data["skin_triangles"]=read_face(args.head)
    np.savez_compressed(args.destination,**data)
