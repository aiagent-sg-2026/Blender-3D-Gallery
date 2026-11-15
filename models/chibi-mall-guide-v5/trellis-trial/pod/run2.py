import os, sys, time
os.environ['ATTN_BACKEND'] = 'xformers'; os.environ['SPCONV_ALGO'] = 'native'
sys.path.insert(0, '/root/TRELLIS')
from PIL import Image
sheet = Image.open('/root/ref/turnaround-b.png').convert('RGB'); W, H = sheet.size; cell = W // 4; bg = sheet.getpixel((5, 5)); views = []
for i in range(4):
    c = sheet.crop((i * cell, 0, (i + 1) * cell, H)); S = max(c.size); sq = Image.new('RGB', (S, S), bg); sq.paste(c, ((S - c.size[0]) // 2, (S - c.size[1]) // 2)); views.append(sq)
from trellis.pipelines import TrellisImageTo3DPipeline
from trellis.utils import postprocessing_utils
pipe = TrellisImageTo3DPipeline.from_pretrained('microsoft/TRELLIS-image-large'); pipe.cuda()
pre = [pipe.preprocess_image(v) for v in views]
sets = {'all4': [0, 1, 2, 3], 'f3q': [0, 1], 'f3qb': [0, 1, 3], 'front': [0]}
ss = {'steps': 12, 'cfg_strength': 7.5}; sl = {'steps': 12, 'cfg_strength': 3}
for name, idx in sets.items():
    for seed in (1, 2, 3, 4):
        if name == 'all4' and seed == 1: continue
        t = time.time(); imgs = [pre[i] for i in idx]
        if len(imgs) > 1: out = pipe.run_multi_image(imgs, seed=seed, preprocess_image=False, sparse_structure_sampler_params=ss, slat_sampler_params=sl)
        else: out = pipe.run(imgs[0], seed=seed, preprocess_image=False, sparse_structure_sampler_params=ss, slat_sampler_params=sl)
        glb = postprocessing_utils.to_glb(out['gaussian'][0], out['mesh'][0], simplify=0.95, texture_size=1024); glb.export(f'/root/out/{name}_s{seed}.glb')
        print('DONE', name, seed, round(time.time() - t, 1), flush=True)
print('ALLDONE', flush=True)
