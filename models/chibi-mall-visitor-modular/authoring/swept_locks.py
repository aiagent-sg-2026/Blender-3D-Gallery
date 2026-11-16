"""Sample the editable, closed hair locks at sculpt and game resolution."""
import math
import numpy as np
from hair_temple_fit import temple, apply

SCALE = 451 / 1.30


def smooth(value, low, high):
    phase = np.clip((value - low) / (high - low), 0, 1)
    return phase**2 * (3 - 2 * phase)


def normalized(vectors):
    return vectors / np.maximum(1e-10, np.linalg.norm(vectors, axis=-1, keepdims=True))


def sample_rings(grid, stations, sides, azimuth=None):
    rows = np.rint(stations * (grid.shape[0] - 1)).astype(int)
    angles = np.arange(sides) * grid.shape[1] / sides if azimuth is None else azimuth * grid.shape[1]
    left = np.floor(angles).astype(int)
    fraction = (angles - left)[None, :, None]
    rings = grid[rows[:, None], left] * (1 - fraction) + grid[rows[:, None], (left + 1) % grid.shape[1]] * fraction
    return np.concatenate((grid[0, :1], rings.reshape(-1, 3), grid[-1, :1]))


def topology(positions, stations, sides, slot, total, azimuth=None):
    ring = 1 + np.arange(len(stations) * sides).reshape(-1, sides)
    end = len(positions) - 1
    faces, charts = [], []
    def add(face, uv):
        faces.append(face)
        charts.append(uv)
    for side in range(sides):
        other = (side + 1) % sides
        u, v = side / sides, (side + 1) / sides
        if azimuth is not None:
            u = azimuth[side]
            v = azimuth[side+1] if side+1 < sides else 1.
        middle = (u + v) / 2
        add((0, ring[0, other], ring[0, side]), ((middle, 0), (v, stations[0]), (u, stations[0])))
        for i in range(len(stations) - 1):
            a, b = ring[i, side], ring[i, other]
            c, d = ring[i+1, side], ring[i+1, other]
            h, k = stations[i:i+2]
            add((a, b, d), ((u, h), (v, h), (v, k)))
            add((a, d, c), ((u, h), (v, k), (u, k)))
        add((ring[-1, side], ring[-1, other], end), ((u, stations[-1]), (v, stations[-1]), (middle, 1)))
    triangles = np.asarray(faces, dtype='i4')
    uv = np.asarray(charts)
    xyz = positions[triangles]
    signed_volume = np.sum(np.cross(xyz[:,1]-xyz[:,0], xyz[:,2]-xyz[:,0]) * (xyz.mean(1)-positions.mean(0)))
    if signed_volume < 0:
        triangles = triangles[:, ::-1]
        uv = uv[:, ::-1]
    rows = math.ceil(total / 6)
    x = .648 + (slot % 6) * (.348 / 6)
    y = .004 + (slot // 6) * (.992 / rows)
    uv = uv * [.348 / 6 - .008, .992 / rows - .017] + [x + .0045, y + .0085]
    return triangles, uv


def assemble(data):
    names = ['Recessed foundation', *data['loftNames'].tolist()]
    high = [data['xyz'] * SCALE]
    low = [data['runtimeXYZ'] * SCALE]
    high_faces, low_faces = [data['triangles']], [data['runtimeTriangles']]
    high_parts, low_parts = [data['piece']], [data['runtimePiece']]
    high_normals, low_normals = [data['normals']], [data['runtimeNormals']]
    color, uv = [data['pigment']], [data['runtimeUV']]
    bindings = {}
    for i, name in enumerate(names[1:]):
        grid = data['loftXYZ'][i]
        normals = data['loftNormals'][i]
        rings, sides = map(int, data['loftTopology'][i])
        stations = np.linspace(.055, .94, rings)
        dense_stations = np.linspace(.011, .982, 58)
        azimuth = data["loftLowAzimuth"][i,:sides] if "loftLowAzimuth" in data else None
        lp = sample_rings(grid, stations, sides, azimuth)
        hp = sample_rings(grid, dense_stations, 26)
        lf, chart = topology(lp, stations, sides, i, len(names) - 1, azimuth)
        hf, _ = topology(hp, dense_stations, 26, i, len(names) - 1)
        offset = sum(map(len, low))
        low_faces.append(lf + offset)
        high_faces.append(hf + sum(map(len, high)))
        low_parts.append(np.full(len(lf), i+1, 'i2'))
        high_parts.append(np.full(len(hf), i+1, 'i2'))
        low.append(lp)
        high.append(hp)
        uv.append(chart)
        low_normals.append(normalized(sample_rings(data.get("loftRuntimeNormals", data["loftNormals"])[i], stations, sides, azimuth)))
        high_normals.append(normalized(sample_rings(normals, dense_stations, 26)))
        color.append(sample_rings(data['loftDye'][i], dense_stations, 26))
        phase = np.r_[0, np.tile(np.cos(2*np.pi*(np.arange(sides)/sides if azimuth is None else azimuth)), rings), 0]
        along = np.r_[0, np.repeat(stations, sides), 1]
        indices = np.arange(len(lp)) + offset
        handles = np.rint(np.linspace(0, grid.shape[0]-1, 8)).astype(int)
        for suffix, sign, edge in [(' outer', 1, 0), (' inner', -1, grid.shape[1]//2)]:
            bindings[name+suffix] = (grid[handles, edge]/SCALE, indices, along, .65+sign*.35*phase)
    high, low = np.concatenate(high), np.concatenate(low)
    high_faces, low_faces = np.concatenate(high_faces), np.concatenate(low_faces)
    high_parts, low_parts = np.concatenate(high_parts), np.concatenate(low_parts)
    high_normals, low_normals = np.concatenate(high_normals), np.concatenate(low_normals)
    # The measurement and each native guide use the same metre scale.
    correction = 451 - low[:,2].max()
    for vertices in (high, low):
        vertices[:,2] += correction * smooth(vertices[:,2], 417, 450)
    for p, _, _, _ in bindings.values():
        p[:,2] += correction * smooth(p[:,2]*SCALE, 417, 450) / SCALE
    def fit(vertices, normals, triangles, parts):
        labels = np.zeros(len(vertices), int)
        labels[triangles.ravel()] = np.repeat(parts, 3)
        hook = names.index('Long outer sweep')
        lower = names.index('Outer lower sweep') if 'Outer lower sweep' in names else -1
        for layer, mask in [('hook', labels==hook), ('lower', labels==lower), ('base', (labels!=hook)&(labels!=lower))]:
            if mask.any():
                vertices[mask], normals[mask] = apply(vertices[mask], normals[mask], lambda v: temple(v, layer))
    fit(high, high_normals, high_faces, high_parts)
    fit(low, low_normals, low_faces, low_parts)
    for key, (p, indices, along, weights) in bindings.items():
        layer = 'hook' if key.startswith('Long outer sweep') else ('lower' if key.startswith('Outer lower sweep') else 'base')
        bindings[key] = (temple(p*SCALE, layer)/SCALE, indices, along, weights)
    return dict(data, xyz=(high/SCALE).astype('f4'), runtimeXYZ=(low/SCALE).astype('f4'),
        triangles=high_faces, runtimeTriangles=low_faces, normals=high_normals.astype('f4'),
        runtimeNormals=low_normals.astype('f4'), pigment=np.uint8(np.clip(np.rint(np.concatenate(color)), 0, 255)),
        runtimeUV=np.concatenate(uv).astype('f4'), piece=high_parts, runtimePiece=low_parts,
        lockBindings=bindings, lockNames=names)
