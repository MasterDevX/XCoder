import os
import sys
import platform

sys.path.append('./System')

from DataBase import PixelType, FileType

SystemName = platform.system()

if SystemName == 'Windows':

	Specifier = ''

else:

	Specifier = '3'

SystemPath = './System/Main.py'
InDecompressedScPath = './In-Decompressed-SC/'
OutCompressedScPath = './Out-Compressed-SC/'
SubPath = [i for i in os.listdir(InDecompressedScPath)]

for i in SubPath:

	CurrentSubPath = i + '/'
	ImagesPath = InDecompressedScPath + '/' + i
	Images = [i for i in os.listdir(ImagesPath)]
	ImagesToCompressPath = [InDecompressedScPath + CurrentSubPath + i for i in Images]
	ImagesToCompress = ' '.join(ImagesToCompressPath)
	OutNameList = [i for i in (Images[0])]
	DotIndex = OutNameList.index('.')
	OutName = ''.join(OutNameList[:DotIndex])
	
	ImagesPixelList = []
	ImagesTypeList = []
	
	for i in Images:
	
		ImagesPixelList.append(str(PixelType[i]))
		ImagesTypeList.append(str(FileType[i]))
	
	ImagesPixelType = ' '.join(ImagesPixelList)
	ImagesFileType = ' '.join(ImagesTypeList)
	
	if '1' in ImagesFileType:

		os.system('python' + Specifier + ' ' + SystemPath + ' ' + ImagesToCompress + ' -p ' + ImagesPixelType + ' -c -header -o ' + OutCompressedScPath + OutName + '.sc')
		
	else:
	
		os.system('python' + Specifier + ' ' + SystemPath + ' ' + ImagesToCompress + ' -p ' + ImagesPixelType + ' -c -header -s -o ' + OutCompressedScPath + OutName + '.sc')