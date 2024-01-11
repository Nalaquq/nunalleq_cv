import os
import shutil

home="/home/nalkuq/nunalleq_cv/"
models=home+"3d_glbs/"

os.chdir(models)
print(os.getcwd())

files=os.listdir()

for x in files:
    if x.__contains__("Uluaq"):
        print(x)
