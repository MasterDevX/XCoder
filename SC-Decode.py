import os
import sys
import lzma
import struct
import random
import binascii
import platform

sys.path.append('./System')

from DataBase import Version
from BytesWorker import *
from PIL import Image

SystemName = platform.system()
sys.stdout.write('\x1b]2;XCoder | Version: ' + Version + ' | Developer: MasterDevX\x07')

if SystemName == 'Windows':

    os.system('cls')

else:

    os.system('clear')

folder = "./In-Compressed-SC/"
folder_export = "./Out-Decompressed-SC/"

def _(message):
    print("[INFO] " + message)

def convert_pixel(pixel, type):
    if type == 0:  # RGB8888
        return struct.unpack('4B', pixel)
    elif type == 2:  # RGB4444
        pixel, = struct.unpack('<H', pixel)
        return (((pixel >> 12) & 0xF) << 4, ((pixel >> 8) & 0xF) << 4,
                ((pixel >> 4) & 0xF) << 4, ((pixel >> 0) & 0xF) << 4)
    elif type == 4:  # RGB565
        pixel, = struct.unpack("<H", pixel)
        return (((pixel >> 11) & 0x1F) << 3, ((pixel >> 5) & 0x3F) << 2, (pixel & 0x1F) << 3)
    elif type == 6:  # LA88
        pixel, = struct.unpack("<H", pixel)
        return ((pixel >> 8), (pixel >> 8), (pixel >> 8), (pixel & 0xFF))
    elif type == 10:  # L8
        pixel, = struct.unpack("<B", pixel)
        return (pixel, pixel, pixel)
    else:
        raise Exception("Unknown pixel type: " + type)

def decompileSC(fileName):
    baseName = os.path.splitext(os.path.basename(fileName))[0]
    
    with open(fileName, "rb") as fh:
        data = fh.read()
        
        if data[0] != 93:
            data = data[26:]

        xbytes = b'\xff\xff\xff\xff\xff\xff\xff\xff'

        data = data[0:5] + xbytes + data[9:]
        decompressed = lzma.LZMADecompressor().decompress(data)
        
        i = 0
        picCount = 0

        _("Collecting information...")
        
        while len(decompressed[i:]) > 5:
            fileType = decompressed[i]
            fileSize, = struct.unpack("<I", decompressed[i + 1:i + 5])
            subType = decompressed[i + 5]
            width, = struct.unpack("<H", decompressed[i + 6:i + 8])
            height, = struct.unpack("<H", decompressed[i + 8:i + 10])
            
            i += 10
            
            if subType == 0:
                pixelSize = 4
            elif subType == 2 or subType == 4 or subType == 6:
                pixelSize = 2
            elif subType == 10:
                pixelSize = 1
            else:
                raise Exception("Unknown pixel type: " + subType)

            _("About: fileName %s, fileType %s, fileSize: %s, subType: %s, width: %s, height: %s" % (fileName, fileType, fileSize, subType, width, height))
            _("Creating picture...")
            
            img = Image.new("RGBA", (width, height))
            
            pixels = []
            
            for y in range(height):
                for x in range(width):
                    pixels.append(convert_pixel(decompressed[i:i + pixelSize], subType))
                    i += pixelSize
            
            img.putdata(pixels)
            
            if fileType == 28 or fileType == 27:
                imgl = img.load()
                iSrcPix = 0
                for l in range(int(height / 32)):
                    for k in range(int(width / 32)):
                        for j in range(32):
                            for h in range(32):
                                imgl[h + (k * 32), j + (l * 32)] = pixels[iSrcPix]
                                iSrcPix += 1
                    for j in range(32):
                        for h in range(width % 32):
                            imgl[h + (width - (width % 32)), j + (l * 32)] = pixels[iSrcPix]
                            iSrcPix += 1
                            
                for k in range(int(width / 32)):
                    for j in range(int(height % 32)):
                        for h in range(32):
                            imgl[h + (k * 32), j + (height - (height % 32))] = pixels[iSrcPix]
                            iSrcPix += 1

                for j in range(height % 32):
                    for h in range(width % 32):
                        imgl[h + (width - (width % 32)), j + (height - (height % 32))] = pixels[iSrcPix]
                        iSrcPix += 1
                        
            fullname = baseName + ('_' * picCount)
                
            _("Saving as png...")
            img.save(folder_export + CurrentSubPath + fullname + ".png", "PNG")
            picCount += 1
            _("Saving completed" + "\n")

files = os.listdir(folder)
for file in files:
	if file.endswith("_tex.sc"):
	
		global CurrentSubPath
	
		ScNameList = []
		for i in file:
			ScNameList.append(i)
		DotIndex = ScNameList.index('.')
		CurrentSubPath = ''.join(ScNameList[:DotIndex]) + '/'
		os.mkdir(folder_export + CurrentSubPath)
		decompileSC(folder + file)
