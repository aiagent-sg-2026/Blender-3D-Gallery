"""Shared planar-cap separation for the reviewed cues and rack bars."""


def mark_planar_caps(mesh):
    """Keep smooth sides separate from two planar ngon end caps."""
    caps = [face for face in mesh.polygons if len(face.vertices) > 4]
    if len(caps) != 2:
        raise ValueError('Expected a closed tapered rod with two ngon caps')
    boundary_edges = {
        mesh.loops[index].edge_index
        for face in caps
        for index in face.loop_indices
    }
    for face in caps:
        face.use_smooth = False
    for index in boundary_edges:
        mesh.edges[index].use_edge_sharp = True
    mesh.update()
    return len(caps), len(boundary_edges)
