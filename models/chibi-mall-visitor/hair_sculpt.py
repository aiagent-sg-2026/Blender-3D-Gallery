"""Swept locks with a rounded cross section and an individually drawn silhouette."""
import math

import bmesh

from face_sculpt import blend_colour, vertex_paint


def sculpt_fringe(mesh, sample, material, rgb, surface):
    chestnut = material("Fringe | soft chestnut", "4E352D", .53)
    chestnut.node_tree.nodes["Principled BSDF"].inputs["IOR"].default_value = 1.43
    shadow, light = rgb("3D2B26"), rgb("61453B")

    def hairline_depth(x, z):
        radius = 1 - (x / .596)**2 - ((z - 2.036) / .589)**2
        cap = .015 - .486 * math.sqrt(max(.040, radius))
        on_temple = min(1, max(0, (abs(x) - .39) / .17))
        # The face profile ends below the crown. Ease off its influence
        # before that point so the upper wave stays continuous.
        face_weight = min(1, max(0, (2.50 - z) / .07))
        envelope = cap + face_weight * min(0, surface(x, z) - .008 - cap)
        return min(envelope, -.070 - .138 * on_temple)

    def lock(name, contour_a, contour_b, projection, thickness, tint):
        edges = list(zip(sample(contour_a, 6), sample(contour_b, 6)))
        vertices, faces, colours = [], [], []
        sections = 20
        for row, (left, right) in enumerate(edges):
            along = row / (len(edges) - 1)
            # Roll the root into a short oval around the side part. At the
            # far end, the drawn contours alone determine the sharp silhouette.
            emerge = min(1.0, along / .22)
            root_width = max(.012, math.sqrt(emerge * (2 - emerge)))
            middle = (left + right) * .5
            left, right = middle.lerp(left, root_width), middle.lerp(right, root_width)
            width = (right - left).length
            relief = .016 + (projection - .016) * emerge
            depth_radius = min(thickness, .39 * width) * (.58 + .42 * emerge)
            for column in range(sections):
                angle = math.tau * column / sections
                u = (1 - math.cos(angle)) / 2
                bulge = math.sin(angle)
                x, z = left.lerp(right, u)
                # A broad, gently offset crest makes one highlight per lock.
                crown = (1.08 - .16 * u) * bulge if bulge > 0 else .34 * bulge
                y = hairline_depth(x, z) - relief - depth_radius * crown
                vertices.append((x, y, z))
                colour = tint + .12 * max(0, bulge) + .04 * along
                colours.append(blend_colour(shadow, light, colour))
        for row in range(len(edges) - 1):
            for column in range(sections):
                a = row * sections + column
                b = row * sections + (column + 1) % sections
                faces.append((a, b, b + sections, a + sections))
        faces.append(tuple(reversed(range(sections))))
        faces.append(tuple(range(len(vertices) - sections, len(vertices))))
        obj = mesh(name, vertices, faces, chestnut)
        normals = bmesh.new()
        normals.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(normals, faces=list(normals.faces))
        normals.to_mesh(obj.data)
        normals.free()
        vertex_paint(obj, chestnut, "Chestnut tone", colours)

    lock("Fringe | left sideburn",
         [(-.34,2.32),(-.48,2.22),(-.543,2.07),(-.524,1.91),(-.431,1.747)],
         [(-.225,2.36),(-.319,2.22),(-.359,2.07),(-.397,1.89),(-.429,1.750)],
         .019,.057,.25)
    lock("Fringe | right sideburn",
         [(.278,2.37),(.348,2.21),(.374,2.03),(.428,1.85),(.421,1.746)],
         [(.41,2.35),(.520,2.20),(.535,2.03),(.505,1.86),(.424,1.749)],
         .020,.053,.26)
    lock("Fringe | temple wing",
         [(.178,2.496),(.322,2.485),(.460,2.395),(.557,2.291),(.650,2.290)],
         [(.242,2.411),(.314,2.349),(.421,2.229),(.567,2.218),(.648,2.287)],
         .030,.051,.45)
    lock("Fringe | right fringe",
         [(.135,2.478),(.214,2.372),(.270,2.240),(.339,2.091),(.331,1.970)],
         [(.294,2.467),(.387,2.392),(.441,2.263),(.433,2.090),(.333,1.973)],
         .053,.065,.34)
    lock("Fringe | shaded diagonal",
         [(.050,2.440),(-.155,2.389),(-.332,2.236),(-.405,2.080),(-.354,1.964)],
         [(.192,2.391),(.048,2.258),(-.107,2.140),(-.254,2.045),(-.352,1.967)],
         .044,.053,.32)
    lock("Fringe | falling bang",
         [(.062,2.499),(.011,2.393),(-.043,2.248),(-.079,2.095),(-.156,1.958)],
         [(.250,2.479),(.235,2.351),(.192,2.197),(.069,2.029),(-.153,1.959)],
         .073,.075,.42)
    lock("Fringe | broad side sweep",
         [(.109,2.535),(-.029,2.555),(-.221,2.504),(-.403,2.386),(-.522,2.250),(-.639,2.218)],
         [(.181,2.453),(.043,2.400),(-.107,2.286),(-.272,2.164),(-.478,2.129),(-.638,2.215)],
         .073,.074,.45)
    lock("Fringe | upper wave",
         [(.080,2.575),(-.048,2.600),(-.211,2.562),(-.357,2.513),(-.472,2.531)],
         [(.164,2.497),(.027,2.504),(-.147,2.466),(-.333,2.438),(-.471,2.527)],
         .073,.045,.41)
