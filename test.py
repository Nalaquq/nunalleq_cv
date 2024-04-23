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
print(co)

light=bpy.data.objects['Light']


def get_vertices(obj):
    '''still need to convert to opencv space and do camera projection'''
    select_obj(obj)
    obj=bpy.data.objects[obj]
    min_x, max_x, min_y, max_y= 1,0,1,0
    vertices=obj.data.vertices[0]
    coordinates=[(obj.matrix_world @ vertices.co) for v in obj.data.vertices]
    coordinates_array=np.array(coords)
    print("I'm getting those vertices \n Here is their shape bro \n")
    print(coordinates_array.shape)
    print("And here is a little sneaky peak of dem vertices \n \n")
    print(coordinates_array)
    print("this is x and y")
    x=coordinates[0]
    y=coordinates[1]
    print(x,y)
    #yolo calculations
    x1=(coordinates[0][0])
    x2=(coordinates[1][0])
    y1=(coordinates[1][1])
    y2=(coordinates[0][1])
    #calulate width/height = center of BBx
    width=(x2-x1)
    height=(y2-y1)
    center_x=x1 + (width/2)
    center_y=y1 + (height/2)
    print("now I'm doing some YOLO calculations...watch me do me!! \n \n")
    text_coordinates= str(center_x) + ' ' +str(center_y) + ' ' +str(width) + ' ' + str(height) + '\n'
    print(text_coordinates) 

get_vertices("Seal_Uluaq_27906")

blender.random_rotate("Seal_Uluaq_27906")

get_vertices("Seal_Uluaq_27906")

'''

def object_drop(object_1, object_2):
    blender.select_obj(object_1)
    #bpy.ops.outliner.item_activate(deselect_all=False)
    #bpy.context.space_data.context = 'PHYSICS'
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.type = 'ACTIVE'
    blender.select_obj(object_2)
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.type = 'PASSIVE'
    bpy.context.object.rigid_body.collision_shape = 'MESH'

selection_names = bpy.context.selected_objects
print (selection_names)


object_drop('Seal_Uluaq_27906', 'Cube')
print(location)

#blender.render_obj(path, 1)





#blender.setRotation()
'''

