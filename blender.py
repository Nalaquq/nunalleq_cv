import bpy

# import one of Alice's cool 3d files
"""eventually this needs to be recompiled as an iterative function that takes the file name of the .glb file, imports it, and selects it for editing"""

bpy.ops.import_scene.gltf(
    filepath="Uluaq_12147.glb",
    files=[{"name": "Uluaq_12147.glb", "name": "Uluaq_12147.glb"}],
    loglevel=50,
)
bpy.ops.object.shade_smooth()

bpy.data.objects["Uluaq_12147"].select_set(True)

# Shades objects (show's 3D model color)
for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        for space in area.spaces:
            if space.type == "VIEW_3D":
                space.shading.type = "MATERIAL"

# Resize the imported 3D object
bpy.ops.transform.resize(
    value=(12.5062, 12.5062, 12.5062),
    orient_type="GLOBAL",
    orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    orient_matrix_type="GLOBAL",
    mirror=False,
    use_proportional_edit=False,
    proportional_edit_falloff="SMOOTH",
    proportional_size=1,
    use_proportional_connected=False,
    use_proportional_projected=False,
    snap=False,
    snap_elements={"INCREMENT"},
    use_snap_project=False,
    snap_target="CLOSEST",
    use_snap_self=True,
    use_snap_edit=True,
    use_snap_nonedit=True,
    use_snap_selectable=False,
)

# Deselect all objects
bpy.ops.object.select_all(action="DESELECT")
# Delete the cube that is autogenerated by Blender
bpy.data.objects["Cube"].select_set(True)
bpy.ops.object.delete(use_global=False, confirm=False)


print(list(bpy.data.objects))
