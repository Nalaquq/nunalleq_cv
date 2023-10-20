
import blenderproc as bproc
import os 
import numpy as np 

print(os.getcwd())
os.chdir('BlenderProc')
bproc.init()

obj=bproc.loader.load_obj("ulu.obj")

# Create a point light next to it

light = bproc.types.Light()

light.set_location([2, -2, 0])

light.set_energy(300)



# Set the camera to be in front of the object

cam_pose = bproc.math.build_transformation_mat([0, -5, 0], [np.pi / 2, 0, 0])

bproc.camera.add_camera_pose(cam_pose)



# Render the scene

# activate normal and depth rendering
bproc.renderer.enable_depth_output(activate_antialiasing=False)
bproc.renderer.enable_normals_output()
bproc.renderer.set_noise_threshold(0.01)  # this is the default value
data = bproc.renderer.render()



# Write the rendering into an hdf5 file

bproc.writer.write_hdf5("output/", data)


