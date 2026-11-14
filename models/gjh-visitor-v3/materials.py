"""glTF-compatible Principled BSDF materials for the v3 visitor."""
import bpy


def mat(name, rgb, rough=.65, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True

    def lin(v):
        v = v / 255
        return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    color = (*map(lin, rgb), 1)
    m.diffuse_color = color
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = color
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    return m


def make_materials():
    return {
        'skin': mat('Warm peach skin', (226, 178, 142), .5),
        'lips': mat('Lips', (204, 142, 126), .5),
        'eye_white': mat('Eye white', (238, 236, 232), .2),
        'iris': mat('Eye iris', (62, 40, 28), .2),
        'pupil': mat('Eye pupil', (12, 10, 10), .1),
        'brow': mat('Brow', (26, 22, 22), .7),
        'hair': mat('Black wavy hair', (24, 21, 22), .55),
        'hoodie': mat('Navy hoodie', (32, 40, 74), .9),
        'hoodie_tape': mat('Hoodie tape', (52, 62, 108), .7),
        'tee': mat('White tee', (240, 240, 236), .85),
        'chino': mat('Khaki chino', (186, 162, 122), .85),
        'shoe': mat('Sneaker upper', (244, 244, 240), .6),
        'sole': mat('Sneaker sole', (226, 224, 216), .7),
        'pack': mat('Backpack black', (30, 32, 34), .75),
        'pack_trim': mat('Backpack trim', (54, 58, 62), .7),
        'lanyard': mat('Lanyard blue', (30, 92, 205), .6),
        'card': mat('Badge card', (238, 240, 244), .5),
        'watch': mat('Watch steel', (150, 154, 160), .35, .6),
    }
