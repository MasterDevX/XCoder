import os
import shutil


def clear_directories():
    for i in ['In', 'Out']:
        for k in ['Compressed', 'Decompressed', 'Sprites']:
            folder = f'SC/{i}-{k}'
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            os.makedirs(folder, exist_ok=True)

    for i in ['In', 'Out']:
        for k in ['Compressed', 'Decompressed']:
            folder = f'CSV/{i}-{k}'
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            os.makedirs(folder, exist_ok=True)
