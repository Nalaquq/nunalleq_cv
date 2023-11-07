import re
import bpy
import os
import random
import os
import argparse
import numpy as np
import time
from tqdm import tqdm

# Create CLI for tool with arg.parse
parser = argparse.ArgumentParser(
    description="A Blender tool for generating synthetic datasets for object detection using 3d assets"
)
# add optional arguments
parser.add_argument(
    "-src",
    "-src_dir",
    type=os.path.abspath,
    help="the source directory containing your data for generation",
)
parser.add_argument(
    "-n",
    "-num",
    type=int,
    help="The number of images to be generated per 3d model. Images angles on the x,y,z plane will be generated randomly",
    default=1000,
)
parser.add_argument(
    "-size",
    type=int,
    help="the size of of object synthetically generated in pixels. Objects will be scaled accoridingly. The default is 1020px.",
    default=1020,
)

args = parser.parse_args()

#init the arguments 
if args.src:
    PATH_MAIN = args.src
else:
    PATH_MAIN = os.path.abspath("3d_glbs")
    print(
        f"\n No source directory given. Main Path set to {PATH_MAIN}. Please use python3 blender.py -h to learn more."
    )


def splitter(path):
    x = os.path.splitext(path)[0]
    print(x)

#import 3d files and select object in blender with material shading
def import_object(path):
    '''imports 3d .glb files and selects the imported object in blender'''
    bpy.ops.import_scene.gltf(
        filepath=path,
        files=[{"name": path, "name": path}],
        loglevel=50,
    )
    bpy.ops.object.shade_smooth()
    # removes the extension of filename for Blender import
    obj = os.path.splitext(path)[0]
    bpy.data.objects[obj].select_set(True)
    # Shades objects (show's 3D model color)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "MATERIAL"


#resize the imported object using a scale factor based on pixel size 
def resize(obj):
    """this function takes the object name and resizes it. The relative size of the transformation should be calculated in pixels if possible to ensure that it does not conflict with syntehtic.py. Blender calculates relative size in meters, but our YOLO classifier will deal in pixels. Thus the resizer is based on a scaled x-height of 1500 pixels"""
    px = 377.9527559055  # one meter is 377.95 pixels
    bpy.data.objects[obj].select_set(True)
    meters = bpy.context.object.dimensions[
        0
    ]  # produces a vector of object size in X,Y,Z Format. We are only taking the measurement for x since we will scale the o   bject by height
    pixels = meters * px
    try:
        x_height = args.size  # might want to change this
        scale_size = x_height // pixels
        print(
            "\n The selected model size is:",
            str(meters),
            "meters",
            "\n This translates to",
            str(pixels),
            "pixels",
            "\n The selected model will be scaled by a factor of:",
            str(scale_size),
        )
    except:
        scale_size = 1500
    bpy.ops.transform.resize(
        value=(scale_size, scale_size, scale_size),
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

#fix so that it rotates along x,y, and z axis
def rotate(obj):
    r = random.uniform(0, 360)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[obj].select_set(True)
    bpy.ops.transform.rotate(value=r, orient_axis='Z')
    bpy.ops.transform.rotate(value=r, orient_axis='Y')
    bpy.ops.transform.rotate(value=r, orient_axis='X')


def delete_cube():
    """deletes the cube that is autogenerated by Blender"""
    try: 
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects["Cube"].select_set(True)
        bpy.ops.object.delete(use_global=False, confirm=False)
    except: 
        pass

def delete_obj(obj):
    try: 
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[obj].select_set(True)
        bpy.ops.object.delete(use_global=False, confirm=False)
    except: 
        pass


def light_aug(intensity):
    """this function augments the position of the light source. The location and light intensity could be randomized"""
    # Delete old light
    bpy.ops.object.select_by_type(type="LIGHT")
    bpy.ops.object.delete(use_global=False)

    view_layer = bpy.context.view_layer

    # Create new light datablock.
    light_data = bpy.data.lights.new(name="New Light", type="POINT")
    light_data.energy = float(intensity)
    print(str(light_data.energy))

    # Create new object with our light datablock.
    light_object = bpy.data.objects.new(name="New Light", object_data=light_data)

    # Link light object to the active collection of current view layer,
    # so that it'll appear in the current scene.
    view_layer.active_layer_collection.collection.objects.link(light_object)

    # Place light to a specified location.
    light_object.location = (7.68889, -6.78579, 4.08386)
    light_object.rotation_euler = (-0.29215, 15.3403, -0.555648)

    # And finally select it and make it active.
    light_object.select_set(True)
    view_layer.objects.active = light_object
    # Sets the location of the light so that object is illuminated
    print(list(bpy.data.objects))




# render a png of image
def render_obj(obj, count):
    """this takes the path e.g., Uluaq_12147" as an argument"""
    # changes the background to white
    number=str(count)
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    # bpy.context.scene.view_settings.view_transform = 'Standard'#bpy.context.scene.render.film_transparent= True
    bpy.context.scene.view_settings.view_transform = "Standard"
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (1, 1, 1, 1)
    bg.inputs[1].default_value = 1.0
    bpy.data.objects[obj].select_set(True)
    bpy.context.scene.render.filepath = obj+"_"+number+"_image.png"
    bpy.ops.render.render(write_still=True)
    # change object color to black for mask
    bpy.ops.object.shade_smooth()
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[obj].select_set(True)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "MATERIAL"
    # creates a black mask of object as well
    led = bpy.data.objects[obj]
    led.animation_data_clear()
    print(str(bpy.data.materials[2]))
    led_mat = bpy.data.materials[2]
    led_mat.use_nodes = True
    tree = led_mat.node_tree
    nodes = tree.nodes
    led_emit = nodes.new("ShaderNodeEmission")
    led_emit.inputs["Color"].default_value = (0, 0, 0, 1)
    led_emit.inputs["Color"].keyframe_insert("default_value", frame=1)
    new_link = tree.links.new(
        nodes["Material Output"].inputs["Surface"],
        nodes["Emission"].outputs["Emission"],
    )
    bpy.context.scene.render.filepath = obj+"_"+number+"_mask.png"
    bpy.ops.render.render(write_still=True)



def init_it(x):
    obj= os.path.splitext(x)[0]
    batch=args.n
    iterator=range(0,batch,1)
    for number in iterator: 
        print(number)
        import_object(x)
        resize(obj)
        rotate(obj)
        delete_cube()
        light_aug(10000)
        render_obj(obj, number)
        delete_obj(obj)


def mk_dir():
    masks_list=[]
    image_list=[]
    home=os.getcwd()
    #creates a list of the subdirectories for each class in the NN dataset
    data_class=os.listdir("data")
    print(data_class)
    ulus="data/ulus"
    ulu_images="data/ulus/images"
    ulu_masks="data/ulus/masks"
    objects=PATH_MAIN
    objects_class=[]
    #gets a list of the differet sub directories containing 3d objects in 3d_glbs directory
    for x in os.listdir(objects):
        objects_class.append(x)
    #goes through each directory in 3d_glbs and iterates the synthetic generation
    for x in objects_class:
        os.chdir(home)
        os.chdir(objects)
        os.chdir(x)
        for x in os.listdir(): 
            try:
                init_it(x)
            except: 
                pass

        

            

    
mk_dir()
#lists=os.listdir("3d_glbs/uluaq")
#os.chdir("3d_glbs/uluaq")
#for file in lists: 
    #init_it(file)

