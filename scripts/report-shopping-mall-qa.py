"""Build human and machine readable findings from measured mall QA evidence."""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def write_csv(path, rows):
    if not rows:
        path.write_text(''); return
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('directory', type=Path)
    directory = parser.parse_args().directory.resolve()
    inventory = read(directory / 'inventory.json')
    execution, preservation = read(directory / 'execution.json'), read(directory / 'preservation.json')
    records, geometry_rows, density_rows = [], [], []
    source_disagreements = []
    warning_codes = Counter()
    for asset in inventory['assets']:
        glb = read(directory / 'glb' / (asset['id'] + '.json'))
        path = directory / 'blender' / (asset['id'] + '.json')
        blender = read(path) if path.exists() else {'phases': {}}
        supplement = directory / 'source-supplements' / (asset['id'] + '.json')
        if supplement.exists():
            blender['phases']['source'] = read(supplement)
        source, delivery = blender['phases'].get('source', {}), blender['phases'].get('glb', {})
        metric = glb['metrics']; flags = []
        for message in glb['validation']['messages']:
            if message['severity'] == 1: warning_codes[message['code']] += 1
        if glb['validation']['numErrors']: flags.append('FORMAT_ERRORS')
        if glb['validation']['numWarnings']: flags.append('VALIDATOR_WARNINGS')
        if not metric['defaultSceneHasMesh']: flags.append('EMPTY_DEFAULT_SCENE')
        if metric['exactZeroAreaTriangles']: flags.append('EXACT_ZERO_AREA_TRIANGLES_DEFAULT_POSE')
        if metric['triangles'] > 100000: flags.append('ABOVE_PROPOSED_100K_TRIANGLE_TARGET')
        if metric['bytes'] > 5 * 1024 * 1024: flags.append('ABOVE_PROPOSED_5_MIB_TARGET')
        if source.get('status') != 'SCANNED': flags.append('SOURCE_SCAN_INCOMPLETE')
        if tuple(source.get('file_version', [])[:2]) > tuple(int(v) for v in blender.get('blender', '5.1').split('.')[:2]): flags.append('SOURCE_FILE_NEWER_THAN_READER')
        if delivery.get('status') != 'SCANNED': flags.append('DELIVERY_SCAN_INCOMPLETE')
        if source.get('mapping', {}).get('root_alias_verified'): flags.append('SOURCE_ROOT_NAME_DIFFERS_FROM_CATALOG')
        per_asset_density = []
        source_boundaries = delivery_welded_boundaries = 0
        for phase, inspection in [('source', source), ('glb', delivery)]:
            for mesh in inspection.get('meshes', []):
                if mesh['status'] != 'SCANNED':
                    flags.append(phase.upper() + '_EVALUATION_ERROR'); continue
                boundary = mesh['raw_topology']['boundary_edges']
                source_boundaries += boundary if phase == 'source' else 0
                welded = mesh.get('position_weld_diagnostic') or {}
                delivery_welded_boundaries += welded.get('boundary_edges', 0) if phase == 'glb' else 0
                geometry_rows.append({'asset': asset['id'], 'phase': phase, 'object': mesh['name'], 'source_type': mesh['source_type'],
                    'triangles': mesh['triangles'], 'exact_zero_area_triangles': mesh['exact_zero_area_triangles'],
                    'boundary_edges_raw': boundary, 'non_manifold_edges_raw': mesh['raw_topology']['non_manifold_edges'],
                    'boundary_edges_position_welded_diagnostic': welded.get('boundary_edges'),
                    'inconsistent_winding_edges_raw': mesh['raw_topology']['inconsistent_winding_edges'],
                    'toolbox_small_or_zero_faces_le_1e_minus8_m2': next((int(r['value']) for r in mesh['print3d_small_or_zero'] if r['name'] == 'Zero Faces'), 0),
                    'uv_layers': ';'.join(mesh['uv_layers'])})
                seen = set()
                for density in mesh['density']:
                    key = (density.get('material'), density.get('image'), density.get('uv_layer'), density.get('width'), density.get('height'), density.get('mapping'))
                    if key in seen: continue
                    seen.add(key)
                    if phase == 'source' and density['status'] != 'MEASURED':
                        source_disagreements.append({'asset': asset['id'], 'object': mesh['name'], 'status': density['status']})
                    row = {'asset': asset['id'], 'phase': phase, 'object': mesh['name'], 'material': density.get('material'),
                           'image': density.get('image'), 'width': density.get('width'), 'height': density.get('height'),
                           'uv_layer': density.get('uv_layer'), 'status': density['status'],
                           'px_per_m_uv_weighted': density.get('density_px_per_m'),
                           'face_min_px_per_m': (density.get('oracle') or {}).get('min'),
                           'face_max_px_per_m': (density.get('oracle') or {}).get('max'), 'mapping': density.get('mapping')}
                    density_rows.append(row)
                    if phase == 'glb': per_asset_density.append(row)
        measured = [r['px_per_m_uv_weighted'] for r in per_asset_density if r['status'] == 'MEASURED']
        density_status = 'N_A_NO_IMAGE_TEXTURES' if metric['images'] == 0 else (
            'MEASURED_TARGET_UNSET' if measured and len(measured) == len(per_asset_density) else 'MEASUREMENT_GAPS')
        if density_status == 'MEASUREMENT_GAPS': flags.append('DELIVERY_TEXTURE_DENSITY_GAPS')
        if any((r.get('width') or 0) > 2048 or (r.get('height') or 0) > 2048 for r in per_asset_density): flags.append('ABOVE_PROPOSED_2048_TEXTURE_TARGET')
        if metric['images'] > 0 and 'texture-free' in asset.get('tags', []): flags.append('TEXTURE_FREE_TAG_WITH_IMAGE_RESOURCES')
        if source_boundaries or delivery_welded_boundaries: flags.append('BOUNDARY_TOPOLOGY_OBSERVED_ROLE_REVIEW')
        declared_triangles = asset.get('declared_metrics', {}).get('triangles')
        if declared_triangles is not None and declared_triangles != metric['triangles']: flags.append('DECLARED_TRIANGLE_METRIC_DIFFERS')
        record = {'id': asset['id'], 'group': asset['group'], 'name': asset['name'], 'file': asset['file'], 'source': asset['source'],
                  'format': 'PASS' if glb['validation']['numErrors'] == 0 and not glb['externalResources'] else 'FAIL',
                  'validator_warnings': glb['validation']['numWarnings'], 'triangles': metric['triangles'], 'bytes': metric['bytes'],
                  'dimensions_m': metric['dimensions'], 'images': metric['images'],
                  'exact_zero_area_triangles': metric['exactZeroAreaTriangles'], 'near_zero_area_triangles_le_1e_minus12_m2': metric['nearZeroAreaTriangles'],
                  'source_boundary_edges_raw': source_boundaries, 'delivery_boundary_edges_welded_diagnostic': delivery_welded_boundaries,
                  'density_status': density_status, 'density_min': min(measured) if measured else None, 'density_max': max(measured) if measured else None,
                  'density_bindings': len(per_asset_density), 'density_measured_bindings': len(measured),
                  'source_status': source.get('status', 'NOT_RUN'), 'delivery_status': delivery.get('status', 'NOT_RUN'),
                  'flags': sorted(set(flags)), 'release_acceptance': 'NOT_RUN'}
        records.append(record)
    primary = [r for r in records if r['group'] == 'shopping-mall']
    summary = {'status': 'REPORT_COMPLETE' if execution['status'] == 'COMPLETE' else 'REPORT_INCOMPLETE',
               'scope': inventory['scope'], 'source_revision': inventory['source_revision'], 'asset_count': len(records),
               'primary_count': len(primary), 'supporting_count': len(records) - len(primary),
               'format_errors_assets': [r['id'] for r in records if r['format'] != 'PASS'],
               'validator_warning_codes': dict(warning_codes),
               'primary_image_textured': sum(r['images'] > 0 for r in primary),
               'primary_image_free': sum(r['images'] == 0 for r in primary),
               'primary_with_exact_zero_triangles': [r['id'] for r in primary if r['exact_zero_area_triangles']],
               'primary_density_gaps': [r['id'] for r in primary if r['density_status'] == 'MEASUREMENT_GAPS'],
               'original_source_density_disagreements': source_disagreements,
               'phase_counts': dict(Counter(p for r in records for p in [r['source_status'], r['delivery_status']])),
               'geometry_objects': len(geometry_rows), 'density_observations': len(density_rows),
               'preservation': preservation, 'duplicate_catalog_records': inventory['duplicate_catalog_records'], 'records': records}
    (directory / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    write_csv(directory / 'assets.csv', [{**r, 'dimensions_m': json.dumps(r['dimensions_m']), 'flags': ';'.join(r['flags'])} for r in records])
    write_csv(directory / 'geometry.csv', geometry_rows)
    write_csv(directory / 'texture-density.csv', density_rows)
    lines = ['# Shopping Mall geometry and texel-density QA', '',
        'Read-only snapshot: 2026-11-15, Asia/Singapore. This is a structural/numeric audit, not release or visual acceptance.', '',
        ('Start with [prioritized findings and causes](findings.md).' if (directory / 'findings.md').exists() else 'Use the measured tables and per-asset evidence below.'), '',
        f"Scanned {len(primary)} Shopping Mall catalog GLBs and {len(records)-len(primary)} supporting/local artifacts. Revision: `{inventory['source_revision']}`.", '',
        f"Format errors: {len(summary['format_errors_assets'])} assets. Textured primary models: {summary['primary_image_textured']}; image-free primary models: {summary['primary_image_free']}.",
        f"Primary models with exact zero-area triangles at the default pose: {len(summary['primary_with_exact_zero_triangles'])}. Primary density measurement gaps: {len(summary['primary_density_gaps'])}.",
        f"Original-input preservation: {preservation['status']}, {preservation['checked_files']} files checked.", '',
        '## Interpretation', '',
        '- Actual density uses decoded image resolution and the assigned material faces in exported geometry. Texel Density Checker 2026.1.1 is checked against a separate world/UV-area oracle. Duplicate image-node bindings with the same mapping are collapsed in the CSV.',
        '- No approved px/m target exists in the current asset contract. Measured ranges are observations, not density PASS/FAIL. Images absent from a GLB mean actual image density is N_A; 1024-based UV references in raw evidence are explicitly hypothetical.',
        '- An asset range can span different images, resolutions, material channels and surface roles. Compare like-for-like image/material usage before setting a target; a broad range alone is not a demonstrated defect.',
        (f"- {len(source_disagreements)} original source density probes disagree with the independent oracle; original states remain in the CSV. Inspect any separate diagnostics before trusting those source values." if source_disagreements else '- Original source density probes did not produce an oracle disagreement.'),
        '- 3D Print Toolbox 1.5.0 solid/degenerate reports are recorded per mesh. Its 0.1 mm small-element threshold is a diagnostic, not proof that a small font/detail is defective. Exact zero-area delivered triangles are listed separately.',
        '- UV/hard-normal seams split GLB vertices. Raw and position-welded topology observations are separate. Welding at 1e-7 m affects disposable diagnostics only and can merge coincident intentional parts; boundary counts require role review, especially text, leaves and visual planes.',
        '- Source curves/modifiers are evaluated with Blender 5.1.2; delivery is independently validated from original GLB bytes, then imported separately. Rootless character sources may contain staging/variants; their counts are not asset-equivalence proof.',
        '- Source file-version tuples include a file-format subversion, not an application patch number. A source with a newer major/minor file format than Blender 5.1 needs matching-version authoring review; this audit does not assert lossless source fidelity.',
        '- 5 MiB, 100k triangles and 2048 image dimensions are proposed review targets from docs/assets.md, not frozen per-asset acceptance gates.',
        '- Sources/exports are not saved or repaired. Preview images, UV readability, shader appearance, animation states, collision, browsers, FPS, rights approval and physical devices are NOT_RUN in this report. Other QA campaigns and publication statuses are unchanged.', '',
        '## Evidence', '',
        '- [Complete records](summary.json), [asset CSV](assets.csv), [per-object geometry CSV](geometry.csv), [texture density CSV](texture-density.csv).',
        '- [Input inventory and hashes](inventory.json), [execution](execution.json), [original-file preservation](preservation.json).',
        ('- [Current Collection/Empty calibration](scanner-calibration-current.json).' if (directory / 'scanner-calibration-current.json').exists() else '- A known-value calibration receipt must be retained separately when reproducing this audit.'),
        ('- [Final verification](verification.json).' if (directory / 'verification.json').exists() else '- Final cross-reader/preservation verification is recorded separately.'),
        ('- [Scanner revision and actor rechecks](scanner-revisions/rechecks.json): initial outputs are retained. Importer-generated bone display geometry is not serialized asset geometry.' if (directory / 'scanner-revisions/rechecks.json').exists() else '- Bone display shapes are suppressed on import; they are not serialized asset triangles.'),
        ('- [Source n-gon area/density diagnostic](source-density-ngon-diagnostic.json).' if (directory / 'source-density-ngon-diagnostic.json').exists() else '- Non-triangular source density needs independent area cross-checking.'),
        '- Each table row links exact GLB structure/validator and Blender source/delivery reports. Source mapping supplements, if present, retain the original unresolved record.', '',
        '## Image-textured primary models', '',
        '| Asset | Images | Measured range px/m | Density state |', '| --- | ---: | ---: | --- |']
    number = lambda value: '—' if value is None else f'{value:,.3f}'
    for r in primary:
        if r['images']: lines.append(f"| {r['id']} | {r['images']} | {number(r['density_min'])}–{number(r['density_max'])} | {r['density_status']} |")
    lines += ['', '## Priority: exact zero-area delivery triangles', '',
        'These are zero results from the raw GLB position/transform area calculation. Blender world-space Float32 evaluation can classify additional very small triangles as zero; those observations stay separate. Clean-up needs a separate change and retest; format conformance alone does not remove these triangles.', '',
              '| Asset | Exact zero triangles | Total triangles | Fraction |', '| --- | ---: | ---: | ---: |']
    for r in sorted((r for r in primary if r['exact_zero_area_triangles']), key=lambda r: -r['exact_zero_area_triangles']):
        lines.append(f"| {r['id']} | {r['exact_zero_area_triangles']:,} | {r['triangles']:,} | {100*r['exact_zero_area_triangles']/r['triangles']:.1f}% |")
    lines += ['', '## Full asset results', '',
              '| Asset | Group | Triangles | KiB | Exact zero triangles | Boundary observation: source / GLB welded | Density | Evidence |',
              '| --- | --- | ---: | ---: | ---: | ---: | --- | --- |']
    for r in records:
        lines.append(f"| {r['id']} | {r['group']} | {r['triangles']:,} | {r['bytes']/1024:.1f} | {r['exact_zero_area_triangles']} | {r['source_boundary_edges_raw']} / {r['delivery_boundary_edges_welded_diagnostic']} | {r['density_status']} | [GLB](glb/{r['id']}.json) · [Blender](blender/{r['id']}.json) |")
    lines += ['', '## Review flags', '', '| Asset | Flags |', '| --- | --- |']
    for r in records:
        if r['flags']: lines.append(f"| {r['id']} | {'; '.join(r['flags'])} |")
    lines += ['', '## Reproduce', '', '```sh',
              'python3 scripts/test-shopping-mall-qa.py /absolute/path/scanner-calibration.json',
              'python3 scripts/qa-shopping-mall.py --output /absolute/path/new-report-directory --workers 2',
              'cp /absolute/path/scanner-calibration.json /absolute/path/new-report-directory/scanner-calibration-current.json',
              'python3 scripts/qa-shopping-mall-source-supplements.py /absolute/path/new-report-directory',
              'python3 scripts/report-shopping-mall-qa.py /absolute/path/new-report-directory', '```', '',
              'Use a new output directory; earlier evidence is not overwritten. Requires repository Node dependencies, Blender and the installed exact P0 extensions. Separate processes, not concurrent bpy threads, provide isolation. Source scripts from model folders are never executed.', '']
    (directory / 'README.md').write_text('\n'.join(lines))
    print(json.dumps({k: v for k, v in summary.items() if k != 'records'}, indent=2))


if __name__ == '__main__':
    main()
