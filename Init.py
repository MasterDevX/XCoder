import os
import sys
import platform

sys.path.append('./System')

from DataBase import Version

SystemName = platform.system()
sys.stdout.write('\x1b]2;XCoder | Version: ' + Version + ' | Developer: MasterDevX\x07')

if SystemName == 'Windows':

    os.system('cls')

else:

    os.system('clear')

os.system('pip3 install pillow')

os.system('mkdir In-Compressed-SC')
os.system('mkdir In-Decompressed-SC')
os.system('mkdir Out-Compressed-SC')
os.system('mkdir Out-Decompressed-SC')
