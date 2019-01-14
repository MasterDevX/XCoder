import os
import sys
import platform

sys.path.append('./System')

SystemName = platform.system()

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
		
Clear()
GameSelect()
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
	
	ImagesPixelType = ' '.join(ImagesPixelList)
	ImagesFileType = ' '.join(ImagesTypeList)
	
	if '1' in ImagesFileType:

		os.system('python' + Specifier + ' ' + SystemPath + ' ' + ImagesToCompress + ' -p ' + ImagesPixelType + ' -c -header -o ' + OutCompressedScPath + OutName + '.sc')
		
	else:
	
		os.system('python' + Specifier + ' ' + SystemPath + ' ' + ImagesToCompress + ' -p ' + ImagesPixelType + ' -c -header -s -o ' + OutCompressedScPath + OutName + '.sc')
