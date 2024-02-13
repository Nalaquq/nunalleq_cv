import blender
import bpy
import numpy as np 


def select_obj(path):
    '''deselects all other objects and selects specified path'''
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[path].select_set(True)


path="Seal_Uluaq_27906"


blender.import_object("Seal_Uluaq_27906.glb")

blender.place_obj("Seal_Uluaq_27906", z=2.0)

bpy.ops.mesh.primitive_plane_add(size=100)
blender.place_obj("Cube", z=0)

ulu=bpy.data.objects['Seal_Uluaq_27906']

##calcualtes the vertices from blender bounding box...need to change to the vertices calculation in eversberg 2021
location=np.array(ulu.location)
bbox=np.array(ulu.bound_box)
print(location)
print(bbox)
#gets all coordinates for a blender object
v=ulu.data.vertices[0]
coords=[(ulu.matrix_world @ v.co) for v in ulu.data.vertices]
co=np.array(coords)
print(co.shape)

'''
#need to fix errors
def get_vertices(obj):
    #select_obj(obj)
    obj=bpy.data.objects(obj)
    vertices=obj.data.vertices[0]
    coordinates=[(obj.matrix_world @ vertices.co) for v in obj.data.vertices]
    coordinates_array=np.array(coords)
    print(coordinates_array.shape)

get_vertices(ulu)
'''
'''
def object_drop(object_1, object_2):
    blender.select_obj(path)
    bpy.ops.outliner.item_activate(deselect_all=True)
    bpy.context.space_data.context = 'PHYSICS'
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.type = 'ACTIVE'
    blender.select_obj(object_2)
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.type = 'PASSIVE'
    bpy.context.object.rigid_body.collision_shape = 'MESH'
'''
  
#blender.render_obj(path, 1)





#blender.setRotation()


