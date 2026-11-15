# Python, MCP and background automation

<!-- KB-SUMMARY-START -->
Use bpy's data API for explicit object/mesh ownership and operators for supported tool actions. An operator depends on mode, active object, selection and sometimes a real editor/region; check `poll()` and the returned status. `Context.temp_override` supplies valid existing context, not a synthetic viewport in background mode. `Object.copy()` shares mesh data until `copy.data = original.data.copy()`; material copies need their own ownership decision. Read world geometry through updated matrices/evaluated data. In Edit Mode use BMesh and flush it. Do not run concurrent bpy access from worker threads; use an external process and bounded main-thread dispatch. For unattended jobs use a separate Blender process, explicit inputs/outputs, `--disable-autoexec` and `--python-exit-code`. These flags are not an OS sandbox. Inspect the installed RNA/API instead of assuming old examples or unversioned MCP documentation match the running version.
<!-- KB-SUMMARY-END -->

## State before mutation

Inspect the file, target collection, active object, selected objects, mode, data users and transforms. A name lookup alone is insufficient when Blender may append `.001`. Capture newly created object references and restrict cleanup to objects the task owns. Preserve the interactive scene when a background job can do the work.

Operators can return `CANCELLED` without producing the desired artifact. Polling is a precondition check; independently inspect the result. This follows the [operator API](https://docs.blender.org/api/current/bpy.ops.html), while the calibration verifies one usable background operator and one unavailable viewport operator.

For evaluated meshes, obtain the dependency graph and use the evaluated object. Temporary meshes belong to their object and need `to_mesh_clear()`; create a persistent mesh explicitly when needed. See [Object.to_mesh](https://docs.blender.org/api/5.0/bpy.types.Object.html) and the [dependency-graph example](https://docs.blender.org/api/5.0/bpy.types.Depsgraph.html); these references are 5.0, not a claim that every signature is unchanged in 5.1.

## Ownership example

```python
copy = original.copy()
target_collection.objects.link(copy)
copy.data = original.data.copy()
# Copy a material only when this instance needs independent shading.
copy.data.materials[0] = original.data.materials[0].copy()
bpy.context.view_layer.update()
```

The [ID API](https://docs.blender.org/api/current/bpy.types.ID.html) explains datablock users. The local probe actually edits shared and independent copies; it does not infer independence from distinct object names.

The connected 5.1.2 API reports `bmesh.update_edit_mesh(mesh, *, loop_triangles=True, destructive=True)`. Flush the edit mesh after BMesh changes; use `destructive=True` when geometry was added or removed. This signature was read from the native callable, not inferred from an older search result.

## Process and thread boundaries

```sh
blender --background --factory-startup --disable-autoexec --threads 2 \
  --python-exit-code 23 --python owned_job.py -- /absolute/output-directory
```

Arguments after `--` belong to the script. Read the [versioned CLI manual](https://docs.blender.org/manual/en/5.1/advanced/command_line/arguments.html) for argument ordering and flags. Avoid applying factory resets to the user's connected interactive Blender.

The [threading guidance](https://docs.blender.org/api/main/info_gotchas_threading.html) warns against Python threads coexisting with Blender execution. Separate downloading/computation from bpy mutation; a network listener should dispatch Blender work through an appropriate main-thread mechanism. This is an execution design recommendation, not a verified property of every MCP server.

For reproducibility, record seeds, versions, source asset hashes and selected roots. Separate rebuilding procedural geometry from exporting a saved edited source. A successful process exit still needs output checks.
