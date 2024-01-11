import subprocess 

def nvidia_check():
    try: 
        subprocess.check_output("nvidia-smi")
        print(subprocess.check_output(['nvidia-smi']).decode())
        #x=subprocess.check_output("nvcc --version")
        #print(x)
        print("Nvidia GPU detected!")
        return True
    except Exception: 
        print("No Nvidia GPU detected")
        return False 

def cuda_enable():
    test=nvidia_check()
    if test==True: 
        print("Enabling CUDA Support")
        import cupy as np
    if test==False: 
        print("No Cuda support detected. \n Image Processing Pipeline will be run on CPU")
        import numpy as np


if __name__== "__main__":
    cuda_enable()



