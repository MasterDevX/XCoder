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
	Images.sort()
	ImagesToCompressPath = [InDecompressedScPath + CurrentSubPath + i for i in Images]
	ImagesToCompressPath.sort()
	ImagesToCompress = ' '.join(ImagesToCompressPath)
	OutNameList = [i for i in (Images[0])]
	DotIndex = OutNameList.index('.')
	OutName = ''.join(OutNameList[:DotIndex])

	while OutName.endswith('_'):

		OutName = OutName[:-1]

	ImagesPixelList = []
	ImagesTypeList = []

	for i in Images:
		try:
			ImagesPixelList.append(str(PixelType[i]))
			ImagesTypeList.append(str(FileType[i]))
		except KeyError:
			print('This .png name is not included in the database. Its either because the database isnt updated yet or your png files are not named properly')                
			answer_keyError = input("IMPORTANT: \nDo you still wish to continue? The compressed .sc file may be broken\n(y/n) ")
			if answer_keyError == "y":
				if "background" and "_tex.png" in i:
					ImagesPixelList.append("0")
					ImagesTypeList.append("1")
				elif "background" and "_tex_.png" in i: #for second background image with _
					ImagesPixelList.append("6")
					ImagesTypeList.append("1")
				else:
					ImagesPixelList.append("0")
					ImagesTypeList.append("28")
			else:
				sys.exit()

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

	if ConvEnable == '1':

		print()

	os.system('python' + Specifier + ' ' + SystemPath + ' ' + ImagesToCompress + ' -p ' + ImagesPixelType + ' -c -header ' + Splitter + '-o ' + OutCompressedScPath + OutName + '.sc')
	print()
