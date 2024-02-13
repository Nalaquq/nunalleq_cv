import bpy, cycles
import os
import random
import argparse
import numpy as np
import time
from tqdm import tqdm
import shutil
import cv2 as cv
import PIL.Image
import shutil
import gpu
from datetime import datetime

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
    default=1,
)
parser.add_argument(
    "-size",
    type=int,
    help="the size of of object synthetically generated in pixels. Objects will be scaled accoridingly. The default is 1500px.",
    default=1500,
)

args = parser.parse_args()

#init the arguments 
if args.src:
    PATH_MAIN = args.src
    os.chdir(PATH_MAIN)
else:
    PATH_MAIN = os.path.abspath(os.getcwd())
    print(
        f"\n No source directory given. Main Path set to {PATH_MAIN}. Please use python3 blender.py -h to learn more."
    )

'''selects both GPU and CPU for rendering engine
'''
#gpu.platform.device_type_get()
bpy.data.scenes[0].render.engine = "CYCLES"

# Set the device_type
bpy.context.preferences.addons[
            "cycles"
            ].preferences.compute_device_type = "CUDA" # or "OPENCL"

# Set the device and feature set
bpy.context.scene.cycles.device = "GPU"

# get_devices() to let Blender detects GPU device
bpy.context.preferences.addons["cycles"].preferences.get_devices()
print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
for d in bpy.context.preferences.addons["cycles"].preferences.devices:
    d["use"] = 1 # Using all devices, include GPU and CPU
    print(d["name"], d["use"])


def spliter(path):
    x = os.path.splitext(path)[0]
    print(x)
    return x 

#import G3d files and select object in blender with material shading
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



def select_obj(path):
    '''deselects all other objects and selects specified path'''
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[path].select_set(True)


def obj_location(path): 
    '''takes object as input and returns a numpy array of x,y,z location values. Note: x,y,z values returned correspond the middle of the object'''
    loc=bpy.data.objects[path].location
    array=np.array(loc)
    return array


def place_obj(obj, **kwargs):
    '''places a selected object at specficied x,y,z coordinates in blender'''
    try: 
        x=kwargs.get('x', int)
        y=kwargs.get('y', int)
        z=kwargs.get('z', int) 
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[obj].select_set(True)
        bpy.context.object.location[2] = z
        bpy.context.object.rotation_quaternion[1] = 1
    except:
        print("Could not place object. Please read documentation.")

def rotateCamera(scene):
    """Rotate the camera around an object. Takes the scene as parameter from handler."""
    newTheta = theta*scene.frame_current
    rotationMatrix = np.array([[math.cos(newTheta),-math.sin(newTheta),0],
                                [math.sin(newTheta), math.cos(newTheta),0],
                                [0,0,1]])
    camera.location = np.dot(cameraOrigin,rotationMatrix) + focusObject.location


def track_obj():
    '''positions the camera to track an object. Must fix handler issue. If run more than once it creates more than one tracking constraint'''
    bpy.data.objects["Camera"].select_set(True)
    bpy.ops.object.constraint_add(type='TRACK_TO')
    bpy.context.object.constraints["Track To"].target = bpy.data.objects["Cube"]
     
def setRotation():
    """ Set handlers to call the rotateCamera function."""
    # clear old handlers
    bpy.app.handlers.frame_change_pre.clear()
    #register a new handler
    bpy.app.handlers.frame_change_pre.append(rotateCamera)
    
def random_rotate(obj):
    rx = random.uniform(-60, 0)
    ry = random.uniform(-180,180)
    rz=random.uniform(-15,90)
    print(rx, ry, rz)
    bpy.context.object.rotation_mode = 'XYZ'
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[obj].select_set(True)
    #bpy.ops.transform.rotate(value=r)
    bpy.ops.transform.rotate(value=rz, orient_axis='Z')
    bpy.ops.transform.rotate(value=ry, orient_axis='Y')
    bpy.ops.transform.rotate(value=rx, orient_axis='X')


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


def light_aug():
    """this function augments the position of the light source. The location and light intensity could be randomized"""
    # Delete old light
    bpy.ops.object.select_by_type(type="LIGHT")
    bpy.ops.object.delete(use_global=False)

    view_layer = bpy.context.view_layer

    # Create new light datablock.
    light_data = bpy.data.lights.new(name="New Light", type="POINT")
    light_data.energy = 30
    print(str(light_data.energy))

    # Create new object with our light datablock.
    light_object = bpy.data.objects.new(name="New Light", object_data=light_data)
    # Link light object to the active collection of current view layer,
    # so that it'll appear in the current scene.
    view_layer.active_layer_collection.collection.objects.link(light_object)
    # Place light to a specified location.
    light_object.location = (7.68889, -6.78579, 4.08386)
    light_object.rotation_euler = (-0.29215, 15.3403, -0.555648)
    bpy.data.lights["New Light"].energy = 1000

    # And finally select it and make it active.
    light_object.select_set(True)
    view_layer.objects.active = light_object
    # Sets the location of the light so that object is illuminated
    print(list(bpy.data.objects))

def cycle_light():
    light = bpy.data.objects['Light']
    light_strength = 0
    light.data.use_nodes = True
    light.data.node_tree.nodes['Emission'].inputs['Strength'].default_value = light_strength

#need to remove materials b/c they are staying with each iteration. 
# render a png of image
def render_obj(obj, label):
    """this takes the path e.g., Uluaq_12147" as an argument"""
    #need to creeate list of from 0-number. Then iterate through this list and render.
    label=str(label)
    time=datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    # changes the background to white
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    # bpy.context.scene.view_settings.view_transform = 'Standard'#bpy.context.scene.render.film_transparent= True
    bpy.context.scene.view_settings.view_transform = "Standard"
    bg = world.node_tree.nodes["Background"]
    bpy.context.scene.render.film_transparent = False
    bg.inputs[0].default_value = (1, 1, 1, 1) 
    bg.inputs[1].default_value = 1.0
    bpy.data.objects[obj].select_set(True)
    bpy.context.scene.render.image_settings.file_format='PNG'  
    bpy.context.scene.render.filepath = obj+"_"+label+"_"+time+"_image"
    bpy.context.scene.render.image_settings.color_mode='RGB' 
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
    # creates a blaccontk mask of object as well
    led = bpy.data.objects[obj]
    led.animation_data_clear()
    mat=[]
    for m in bpy.data.materials:
        mat.append(m)
    print(mat)
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
    bpy.context.scene.render.image_settings.file_format='PNG'
    bpy.context.scene.render.filepath = obj+"_"+label+"_"+time+"_mask"
    bpy.context.scene.render.image_settings.color_mode='RGB'
    bpy.ops.render.render(write_still=True) 
    bpy.data.materials.remove(led_mat)
    delete_obj(obj)

def mk_dir():
    home=os.getcwd()
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
            print(x)
    

def generate(path):
    obj=spliter(path)
    batch=args.n
    iterator=range(0,batch,1)
    for number in iterator: 
        import_object(path)
        resize(obj)
        random_rotate(obj)
        delete_cube()
        #light_aug()
        cycle_light()
        render_obj(obj, number)
        delete_obj(obj)
        print

source = PATH_MAIN
destination_images = '/home/nalkuq/nunalleq_cv/blender_images/'
destination_masks = "/home/nalkuq/nunalleq_cv/blender_masks/"

def iteration():
    os.chdir(source)
    for x in os.listdir():
        if x.endswith(".glb"):
            generate(x)
        file_mover()
    mask_fix()
    denoise()


def file_mover():
    os.chdir(source)
    for x in os.listdir():
        if x.endswith("mask.png"):
            print(x)
            src_path = os.path.join(source, x)
            dst_path = os.path.join(destination_masks, x)
            shutil.move(src_path, dst_path)
            os.chdir(source)
        if x.endswith("image.png"): 
            print(x)
            src_path = os.path.join(source, x)
            dst_path = os.path.join(destination_images, x)
            shutil.move(src_path, dst_path)
            os.chdir(source)


def mask_fix():
    '''Blender rendered mask.png files have errors. This function rests the .png file so that it works with synthetic.py'''
    os.chdir(destination_masks)
    for x in os.listdir():
        image=PIL.Image.open(x)
        rgba=image.convert("RGBA")
        datas=rgba.getdata()
        newData=[]
        for item in datas:
            if item[0]!=255 and item[1]!=255 and item[2]!=255:
                newData.append((0,0,0,1))
            else: 
                newData.append(item)
        rgba.putdata(newData)
        rgba.save(x, "PNG")
        print(image)
    os.chdir(source)

#denoises image to remove black pixels around border of mask 
def denoise():
    os.chdir(destination_masks)
    for x in os.listdir():
        filename=x
        img = cv.imread(x, cv.IMREAD_GRAYSCALE)
        assert img is not None, "file could not be read, check with os.path.exists()"
        kernel = np.ones((5,5),np.uint8)
        opening = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
        cv.imwrite(filename, opening)
        print(x)
    os.chdir(source)

if __name__ == "__main__":
    iteration()
    



