from agent import train
from pathlib import PurePath
import shutil
import os

if __name__ == '__main__':
    relative_dir = (str(PurePath(__file__).parent))
    if(os.path.isdir(relative_dir + "\__pycache__")):
        shutil.rmtree(relative_dir + "\__pycache__")
    if(os.path.isdir(relative_dir + "\model")):
        shutil.rmtree(relative_dir + "\model")
    
    train()