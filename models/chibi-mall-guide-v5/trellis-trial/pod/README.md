# Pod scripts (as run on 2026-11-15)

Runpod secure-cloud RTX 4090, image `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`, container disk 60 GB, port 8000/http for fetching results with `curl`.
`setup_all.sh` and `run2.py` are the exact files written onto the pod (reproduced below); `exec-pod` was used to run them in the background and poll logs.

## setup_all.sh
```sh
set -x
export DEBIAN_FRONTEND=noninteractive
cd /root
git clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/microsoft/TRELLIS.git
wget -q -O /root/ref/turnaround-b.png https://raw.githubusercontent.com/yapweijun1996/Blender-3D-Gallery/main/models/chibi-mall-guide-v5/reference/turnaround-b.png
(apt-get update -qq; apt-get install -y -qq libegl1 libgl1 libgles2 libglib2.0-0 libxrender1 libusb-1.0-0 libx11-6 libxext6 libsm6 libgomp1 libxi6 libxrandr2) > /root/apt.log 2>&1 &
pip install --ignore-installed blinker
pip install pillow imageio imageio-ffmpeg tqdm easydict opencv-python-headless scipy ninja rembg onnxruntime trimesh open3d xatlas pyvista pymeshfix igraph transformers
cd /root/TRELLIS
. ./setup.sh --basic --xformers --diffoctreerast --spconv --mipgaussian --nvdiffrast
pip install /tmp/extensions/nvdiffrast --no-build-isolation
pip install --no-deps xformers==0.0.28.post1 --index-url https://download.pytorch.org/whl/cu124
sed -i 's/xops\.fmha\.BlockDiagonalMask/xops.fmha.attn_bias.BlockDiagonalMask/g' trellis/modules/sparse/attention/full_attn.py trellis/modules/sparse/attention/serialized_attn.py trellis/modules/sparse/attention/windowed_attn.py
# stub: TRELLIS only imports kaolin.utils.testing.check_tensor
D=/usr/local/lib/python3.11/dist-packages/kaolin; mkdir -p $D/utils; touch $D/__init__.py $D/utils/__init__.py; printf 'def check_tensor(*a, **k):\n    return True\n' > $D/utils/testing.py
wait
```

## run2.py
Loads `microsoft/TRELLIS-image-large` once, crops the four views of the reference sheet (front, three-quarter, side, back) to squares, pre-processes them once, and for the view sets `all4` (0,1,2,3), `f3q` (0,1), `f3qb` (0,1,3) and `front` (0) and seeds 1 to 4 calls `run_multi_image` (or `run` for one view) with `preprocess_image=False`, sparse-structure sampler steps 12 / cfg 7.5, slat sampler steps 12 / cfg 3, then `postprocessing_utils.to_glb(gaussian, mesh, simplify=0.95, texture_size=1024)` and exports `/root/out/<set>_s<seed>.glb`. About 24 seconds per run on the 4090; 15 runs, plus seed 1 of `all4` from the first trial. Environment: `ATTN_BACKEND=xformers`, `SPCONV_ALGO=native`.
