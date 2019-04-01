import os
import sys
import platform
from PIL import Image

sys.path.append('./System')

from DataBase import Version

SystemName = platform.system()
sys.stdout.write('\x1b]2;XCoder | Version: ' + Version + ' | Developer: MasterDevX\x07')

if SystemName == 'Windows':

	Specifier = ''

	def Clear():

		os.system('cls')

else:

	Specifier = '3'

	def Clear():

		os.system('clear')

def GameSelect():

	global PixelType, FileType

	print('1 - Brawl Stars')
	Game = input('Select Target Game: ')

	if Game == '1':

		from DataBase import PixelTypeBS as PixelType
		from DataBase import FileTypeBS as FileType

	else:

		Clear()
		GameSelect()

def Conversion():

	global ConvEnable

	print('1 - Yes')
	print('2 - No')
	ConvEnable = input('Choose if 32bit image conversion will be forced: ')

	if ConvEnable != '1' and ConvEnable != '2':

		Clear()
		Conversion()

Clear()
GameSelect()
Clear()
Conversion()
Clear()

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

		if ConvEnable == '1':

			print('[INFO] Converting ' + i + ' to 32bit image...')
			ConvImage = Image.open(InDecompressedScPath + CurrentSubPath + i).convert('RGBA')
			ConvImage.save(InDecompressedScPath + CurrentSubPath + i)

	ImagesPixelType = ' '.join(ImagesPixelList)
	ImagesFileType = ' '.join(ImagesTypeList)

	if '1' in ImagesFileType:

		Splitter = ''

	else:

		Splitter = '-s '

	os.system('python' + Specifier + ' ' + SystemPath + ' ' + ImagesToCompress + ' -p ' + ImagesPixelType + ' -c -header ' + Splitter + '-o ' + OutCompressedScPath + OutName + '.sc')
