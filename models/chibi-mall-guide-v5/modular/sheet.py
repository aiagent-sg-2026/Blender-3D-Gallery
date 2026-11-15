"""Join view0..3.png of a folder into sheet.png. Run: blender --background --factory-startup --python sheet.py -- DIR"""
import bpy, sys, numpy as np
d = sys.argv[sys.argv.index('--') + 1]; ims = [bpy.data.images.load(f'{d}/view{i}.png') for i in range(4)]; n = ims[0].size[0]
W = bpy.data.images.new('s', n * 4, n); W.pixels = np.concatenate([np.array(i.pixels[:]).reshape(n, n, 4) for i in ims], axis=1).ravel().tolist(); W.filepath_raw = f'{d}/sheet.png'; W.file_format = 'PNG'; W.save()
