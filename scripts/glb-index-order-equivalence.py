"""Compare triangle GLBs allowing only index submission order to differ."""
import json
import struct


def compare_index_order_only(reference, candidate):
    def unpack(data):
        assert data[:4] == b'glTF' and int.from_bytes(data[4:8], 'little') == 2
        assert int.from_bytes(data[8:12], 'little') == len(data)
        length = int.from_bytes(data[12:16], 'little')
        assert data[16:20] == b'JSON' and data[24+length:28+length] == b'BIN\x00'
        return json.loads(data[20:20+length]), data[28+length:]

    before, a = unpack(reference)
    after, b = unpack(candidate)
    assert before == after, 'Full JSON, identities, materials or bindings changed'
    assert len(a) == len(b)
    regions = set()
    triangles = 0
    for mesh in before['meshes']:
        for primitive in mesh['primitives']:
            assert primitive.get('mode', 4) == 4
            accessor = before['accessors'][primitive['indices']]
            view = before['bufferViews'][accessor['bufferView']]
            size = {5123: 2, 5125: 4}[accessor['componentType']]
            assert accessor['type'] == 'SCALAR' and accessor['count'] % 3 == 0
            assert view.get('byteStride', size) == size
            start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
            end = start + accessor['count'] * size
            regions.add((start, end))
            fmt = '<' + ('H' if size == 2 else 'I') * accessor['count']

            def oriented(data):
                ids = struct.unpack_from(fmt, data, start)
                rows = []
                for i in range(0, len(ids), 3):
                    x, y, z = ids[i:i+3]
                    rows.append(min((x, y, z), (y, z, x), (z, x, y)))
                return sorted(rows)

            assert oriented(a) == oriented(b), 'Oriented triangles or multiplicity changed'
            triangles += accessor['count'] // 3
    cursor = 0
    for start, end in sorted(regions):
        assert start >= cursor, 'Unexpected overlapping index regions'
        assert a[cursor:start] == b[cursor:start], 'Non-index payload changed'
        cursor = end
    assert a[cursor:] == b[cursor:], 'Trailing non-index payload changed'
    return dict(exact_bytes=reference == candidate, full_json_unchanged=True,
                all_non_index_bytes_unchanged=True, oriented_triangles_unchanged=True,
                mesh_primitive_triangle_count=triangles)
