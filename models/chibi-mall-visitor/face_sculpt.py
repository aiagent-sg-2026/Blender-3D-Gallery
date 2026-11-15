"""Shape the cheek plane and build a recessed, continuous mouth in the head mesh."""
import math

from mathutils import Vector


def cheek_volume(x, z):
    return .029 * math.exp(-((abs(x) - .317) / .147) ** 2 - ((z - 1.714) / .086) ** 2)


def blush_weight(x, z):
    height = z - 1.704 - .14 * (abs(x) - .325)
    return math.exp(-((abs(x) - .325) / .166) ** 2 - (height / .085) ** 2)


def blend_colour(first, second, weight):
    return tuple(a + (b - a) * weight for a, b in zip(first, second))


def vertex_paint(obj, material, attribute, colours):
    layer = obj.data.color_attributes.new(name=attribute, type="FLOAT_COLOR", domain="POINT")
    for index, colour in enumerate(colours):
        layer.data[index].color = (*colour, 1)
    material_nodes = material.node_tree
    if material_nodes.nodes.get(attribute):
        return
    node = material_nodes.nodes.new("ShaderNodeVertexColor")
    node.name = attribute
    node.layer_name = attribute
    material_nodes.links.new(node.outputs["Color"], material_nodes.nodes["Principled BSDF"].inputs["Base Color"])


def smile_outline(angle):
    """The raised corners widen above the centre of the lower lip."""
    controls = [
        (.100, 1.631), (.093, 1.646), (.059, 1.642), (.002, 1.639),
        (-.061, 1.641), (-.093, 1.645), (-.100, 1.629), (-.087, 1.595),
        (-.062, 1.562), (-.027, 1.538), (.011, 1.536), (.049, 1.547),
        (.077, 1.570), (.094, 1.600),
    ]
    count = len(controls)
    position = (angle % math.tau) * count / math.tau
    index = int(position)
    t = position - index
    a, b, c, d = [Vector(controls[(index+k) % count]) for k in (-1, 0, 1, 2)]
    return .5 * (2*b + (-a+c)*t + (2*a-5*b+4*c-d)*t*t + (-a+3*b-3*c+d)*t**3)


def closed_strip(faces, outer, inner):
    for i, a in enumerate(outer):
        j = (i + 1) % len(outer)
        faces.append((a, outer[j], inner[j], inner[i]))


def stitch_perimeters(faces, outer, inner, vertices, centre):
    """Join an existing jaw grid to an evenly sampled lip without T-junctions."""
    def polar(index):
        x, _, z = vertices[index]
        return math.atan2(z - centre.y, x - centre.x) % math.tau

    outer = sorted(outer, key=polar)
    inner = sorted(inner, key=polar)
    i = j = 0
    while i < len(outer) or j < len(inner):
        a, b = outer[i % len(outer)], inner[j % len(inner)]
        next_a = outer[(i + 1) % len(outer)]
        next_b = inner[(j + 1) % len(inner)]
        angle_a = polar(next_a) + (math.tau if i + 1 >= len(outer) else 0)
        angle_b = polar(next_b) + (math.tau if j + 1 >= len(inner) else 0)
        if j == len(inner) or (i < len(outer) and angle_a <= angle_b):
            faces.append((a, next_a, b))
            i += 1
        else:
            faces.append((a, next_b, b))
            j += 1


def sculpt_head(profile, surface, mesh, skin, new_material, rgb):
    sectors = 68
    middle = 3 * sectors // 4
    left, right = middle - 5, middle + 5
    lower = next(i for i, p in enumerate(profile) if p.x >= 1.493)
    upper = next(i for i, p in enumerate(profile) if p.x >= 1.706)
    vertices, faces, colours = [], [], []
    cream, rose = rgb("FFD0AE"), rgb("F19C8D")

    def complexion(x, z, front):
        return blend_colour(cream, rose, .61 * front * blush_weight(x, z))

    def add(x, y, z, colour):
        vertices.append((x, y, z))
        colours.append(colour)
        return len(vertices) - 1

    for z, rx, ry, cy in profile:
        for j in range(sectors):
            angle = math.tau * j / sectors
            c, s = math.cos(angle), math.sin(angle)
            x = rx * math.copysign(abs(c) ** (2 / 2.6), c)
            y = cy + ry * math.copysign(abs(s) ** (2 / 2.6), s)
            if s < 0:
                y = surface(x, z)
            add(x, y, z, complexion(x, z, max(0, -s) ** .8))

    for i in range(len(profile) - 1):
        for j in range(sectors):
            if lower <= i < upper and left <= j < right:
                continue
            a = i * sectors + j
            b = i * sectors + (j + 1) % sectors
            faces.append((a, b, b + sectors, a + sectors))
    faces.append(tuple(reversed(range(sectors))))
    faces.append(tuple(range(len(vertices) - sectors, len(vertices))))

    outer = [i * sectors + j for i in range(lower, upper + 1)
             for j in range(left, right + 1) if i in (lower, upper) or j in (left, right)]
    centre = Vector((0, 1.594))
    outline = [smile_outline(math.tau * k / 64) for k in range(64)]
    # Intermediate rings sample the curved cheeks before they roll into the lip.
    outer.sort(key=lambda i: math.atan2(vertices[i][2]-centre.y, vertices[i][0]-centre.x))
    def intersect_border(edge):
        direction = (edge - centre).normalized()
        for i, first in enumerate(outer):
            second = outer[(i + 1) % len(outer)]
            ax, _, az = vertices[first]
            bx, _, bz = vertices[second]
            border = Vector((bx - ax, bz - az))
            divisor = direction.cross(border)
            if abs(divisor) < 1e-9:
                continue
            origin = Vector((ax, az)) - centre
            distance = origin.cross(border) / divisor
            fraction = origin.cross(direction) / divisor
            if distance > 0 and -.00001 <= fraction <= 1.00001:
                return centre + direction * distance
        raise ValueError("Mouth perimeter is outside the facial opening")

    targets = [intersect_border(edge) for edge in outline]
    previous = []
    for progress in (.10, .27, .45, .63, .81):
        ring = []
        for target, edge in zip(targets, outline):
            x, z = target.lerp(centre + 1.22 * (edge - centre), progress)
            ring.append(add(x, surface(x, z), z, complexion(x, z, 1)))
        if previous:
            closed_strip(faces, previous, ring)
        else:
            stitch_perimeters(faces, outer, ring, vertices, centre)
        previous = ring
    # A rolled skin edge leads to a red inner lip and then the deep rear wall.
    for scale, depth, colour, tint in [
        (1.22, 0, cream, 0), (1.085, -.0012, rgb("F7B296"), .24),
        (1.015, -.002, rgb("EB967D"), .48), (.994, -.001, rgb("CB6C54"), .64),
        (.98, .004, rgb("B45043"), .88), (.94, .014, rgb("953B31"), 1),
        (.845, .026, rgb("A13D2E"), 1), (.63, .036, rgb("93382C"), 1),
        (.32, .040, rgb("923D2F"), 1),
    ]:
        ring = []
        for edge in outline:
            x, z = centre + scale * (edge - centre)
            colour_here = blend_colour(complexion(x, z, 1), colour, tint)
            ring.append(add(x, surface(x, z) + depth, z, colour_here))
        if previous:
            closed_strip(faces, previous, ring)
        else:
            stitch_perimeters(faces, outer, ring, vertices, centre)
        previous = ring
    centre_id = add(centre.x, surface(*centre) + .042, centre.y, rgb("923D2F"))
    for i, index in enumerate(previous):
        faces.append((index, previous[(i + 1) % len(previous)], centre_id))

    # Compact away the original grid samples that lay inside the opening.
    used = sorted({index for polygon in faces for index in polygon})
    remap = {old: new for new, old in enumerate(used)}
    face_material = skin.copy()
    face_material.name = "Face | complexion and inner lip"
    face = mesh("Porcelain | sculpted jaw", [vertices[i] for i in used],
                [tuple(remap[i] for i in polygon) for polygon in faces], face_material)
    vertex_paint(face, face_material, "Complexion", [colours[i] for i in used])

    # Domed dental and tongue surfaces are inside the opening. The lip occludes
    # their sides as the camera turns. Both are built in face coordinates.
    def inset(name, material, width, top, bottom, back, rise):
        verts, polys = [], []
        steps = 32
        for row in range(7):
            t = row / 6
            for column in range(steps + 1):
                u = 2 * column / steps - 1
                x = u * width
                z = bottom(u) * (1 - t) + top(u) * t
                depth = back - rise * (1 - u*u) * math.sin(math.pi*t)
                verts.append((x, surface(x, z) + depth, z))
        for row in range(6):
            for col in range(steps):
                a = row * (steps + 1) + col
                polys.append((a, a + 1, a + steps + 2, a + steps + 1))
        return mesh(name, verts, polys, material)

    enamel = new_material("Enamel | warm ivory", "FFF0D9", .36)
    inset("Smile | upper teeth", enamel, .090, lambda u: 1.654 + .007*u*u,
          lambda u: 1.621 + .030*u*u, .005, .002)
    coral = new_material("Tongue | coral", "FF947B", .53)
    tongue = inset("Smile | tongue", coral, .095, lambda u: 1.591 - .020*u*u + .0015*u,
                   lambda u: 1.524 + .018*u*u, .014, .007)
    gradient = [blend_colour(rgb("FFAC90"), rgb("E57867"),
                            max(0, min(1, (v.co.z - 1.54) / .065)))
                for v in tongue.data.vertices]
    vertex_paint(tongue, coral, "Tongue colour", gradient)
