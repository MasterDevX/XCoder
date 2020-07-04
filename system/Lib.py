try:
    import io
    import os
    import sys
    import time
    import json
    import struct
    import shutil
    import hashlib
    import platform
    import traceback
    import subprocess
    import colorama
    from PIL import Image, ImageDraw
except: pass

Version = '2.0.0 beta'

lzham_path = 'system\\lzham'

isWin = platform.system() == "Windows"

nul = f" > {'nul' if isWin else '/dev/null'} 2>&1"

if isWin:

    try: colorama.init()
    except: pass

    import ctypes
    Title = ctypes.windll.kernel32.SetConsoleTitleW
    del ctypes

    def Clear():
        os.system('cls')

else:

    def Title(message):
        sys.stdout.write(f"\x1b]2;{message}\x07")

    def Clear():
        os.system('clear')

def locale(lang):
    global string
    from system.strings import string
    string = string[lang]


def info(message):
    print(f"[INFO] {message}")

def progressbar(message, current, total, start = 0, end = 100):
    sys.stdout.write(f"\r[{((current + 1) * end + start) // total + start}%] {message}")

def percent(current, total):
    return (current + 1) * 100 // total

def int_qu(a):
    try:
        return int(input(f"[????] {a} "))
    except:
        return int_qu(a)

def question(message):
    x = input(f"[????] {message} [y/n] ").lower()
    return "ny".index(x) if x in ("y", "n") else question(message)

def err_text(message):
    print(colorama.Fore.RED + message + colorama.Style.RESET_ALL)

def done_text(message):
    print(colorama.Fore.GREEN + message + colorama.Style.RESET_ALL)

def write_log(err):
    if not os.path.isfile('log.txt'):
        mode = 'w'
    else:
        mode = 'a'
    log = open('log.txt', mode, encoding='utf-8')
    log.write(string.got_error % (time.strftime('%d.%m.%Y %H:%M:%S'), err))
    log.close()

def pixelsize(type):
    if type in (0, 1):
        return 4
    if type in (2, 3, 4, 6):
        return 2
    if type in (10,):
        return 1
    raise Exception(string.unk_type % type)
    
def format(type):
    if type in range(4):
        return 'RGBA'
    if type in (4,):
        return 'RGB'
    if type in (6,):
        return 'LA'
    if type in (10,):
        return 'L'
    raise Exception(string.unk_type % type)

def bytes2rgba(data, type, img, pix):

    if type in (0, 1):
        def readpixel():
            return struct.unpack('4B', data.read(4))
    elif type == 2:
        def readpixel():
            p, = struct.unpack('<H', data.read(2))
            return ((p >> 12 & 15) << 4, (p >> 8 & 15) << 4, (p >> 4 & 15) << 4, (p >> 0 & 15) << 4)
    elif type == 3:
        def readpixel():
            p, = struct.unpack('<H', data.read(2))
            return ((p >> 11 & 31) << 3, (p >> 6 & 31) << 3, (p >> 1 & 31) << 3, (p & 255) << 7)
    elif type == 4:
        def readpixel():
            p, = struct.unpack("<H", data.read(2))
            return ((p >> 11 & 31) << 3, (p >> 5 & 63) << 2, (p & 31) << 3)
    elif type == 6:
        def readpixel():
            return struct.unpack("2B", data.read(2))[::-1]
    elif type == 10:
        def readpixel():
            return struct.unpack("B", data.read(1))

    width, height = img.size
    point = -1
    for y in range(height):
        for x in range(width):
            pix.append(readpixel())

        curr = percent(y, height)
        if curr > point:
            progressbar(string.crt_pic, y, height)
            point = curr

    img.putdata(pix)


def rgba2bytes(sc, img, type):


    if type in (0, 1):
        def writepixel(pixel):
            return struct.pack('4B', *pixel)
    if type == 2:
        def writepixel(pixel):
            r, g, b, a = pixel
            return struct.pack('<H', a >> 4 | b >> 4 << 4 | g >> 4 << 8 | r >> 4 << 12)
    if type == 3:
        def writepixel(pixel):
            r, g, b, a = pixel
            return struct.pack('<H', a >> 7 | b >> 3 << 1 | g >> 3 << 6 | r >> 3 << 11)
    if type == 4:
        def writepixel(pixel):
            r, g, b = pixel
            return struct.pack('<H', b >> 3 | g >> 2 << 5 | r >> 3 << 11)
    if type == 6:
        def writepixel(pixel):
            return struct.pack('2B', *pixel[::-1])
    if type == 10:
        def writepixel(pixel):
            return struct.pack('B', *pixel)

    width, height = img.size

    pix = img.load()
    point = -1
    for y in range(height):
        for x in range(width):
            sc.write(writepixel(pix[x, y]))

        curr = percent(y, height)
        if curr > point:
            progressbar(string.writing_pic, y, height)
            point = curr


def join_image(img, p):
    _w, _h = img.size
    imgl = img.load()
    x = 0
    a = 32

    _ha = _h // a
    _wa = _w // a
    ha = _h % a

    for l in range(_ha):
        for k in range(_w // a):
            for j in range(a):
                for h in range(a):
                    imgl[h + k * a, j + l * a] = p[x]
                    x += 1

        for j in range(a):
            for h in range(_w % a):
                imgl[h + (_w - _w % a), j + l * a] = p[x]
                x += 1
        progressbar(string.join_pic, l, _ha)

    for k in range(_wa):
        for j in range(_h % a):
            for h in range(a):
                imgl[h + k * a, j + (_h - _h % a)] = p[x]
                x += 1

    for j in range(ha):
        for h in range(_w % a):
            imgl[h + (_w - _w % a), j + (_h - _h % a)] = p[x]
            x += 1
    progressbar(string.join_pic, l, _ha)

def split_image(img):
    p = []
    _w, _h = img.size
    imgl = img.load()
    a = 32
    
    _ha = _h // a
    _wa = _w // a
    ha = _h % a
    
    for l in range(_ha):
        for k in range(_wa):
            for j in range(a):
                for h in range(a):
                    p.append(imgl[h + (k * a), j + (l * a)])

        for j in range(a):
            for h in range(_w % a):
                p.append(imgl[h + (_w - (_w % a)), j + (l * a)])
        progressbar(string.split_pic, l, _ha)

    for k in range(_w // a):
        for j in range(int(_h % a)):
            for h in range(a):
                p.append(imgl[h + (k * a), j + (_h - (_h % a))])

    for j in range(ha):
        for h in range(_w % a):
            p.append(imgl[h + (_w - (_w % a)), j + (_h - (_h % a))])
    img.putdata(p)
    progressbar(string.split_pic, l, _ha)

class Reader:
    def __init__(self, data):
        self.stream = io.BytesIO(data)

    @property
    def byte(self):
        return int.from_bytes(self.stream.read(1), 'little')

    @property
    def uint16(self):
        return int.from_bytes(self.stream.read(2), 'little')

    @property
    def int16(self):
        return int.from_bytes(self.stream.read(2), 'little', signed = True)

    @property
    def uint32(self):
        return int.from_bytes(self.stream.read(4), 'little')

    @property
    def int32(self):
        return int.from_bytes(self.stream.read(4), 'little', signed = True)

    def string(self, length=1):
        return self.stream.read(int.from_bytes(self.stream.read(length), 'little')).decode()

def decompileSC(fileName, CurrentSubPath, to_memory=False, folder=None, folder_export=None):
    pngs = []
    picCount = 0
    scdata = io.BytesIO()
    
    info(string.collecting_inf)
    with open(fileName, "rb") as fh:
        start = fh.read(6)
        if start == b'SC\x00\x00\x00\x01':
            fh.read(20)
            start = b''
        data = start + fh.read()

        try:
            uselzham = False
            if data[:4] == b'SCLZ':
                try:
                    from lzham import decompress as d
                except:
                    if not isWin:
                        return info(string.not_installed2 % 'LZHAM')
                    with open('temp.sc', 'wb') as sc:
                        sc.write(b'LZH\x30' + data[4:9] + bytes(4) + data[9:])
                    if os.system(f'{lzham_path} -d{data[4]} -c d temp.sc _temp.sc{nul}'):
                        raise Exception(string.decomp_err)
                    data = open('_temp.sc', 'rb').read()
                    [os.remove(i) for i in ('temp.sc', '_temp.sc')]
                else:
                    dict_size, data_size = struct.unpack("<BI", data[4:9])
                    data = d(data[9:], data_size, {"dict_size_log2": dict_size})
                info(string.detected_comp % 'LZHAM')
                uselzham = True
            else:
                try:
                    from lzma import LZMADecompressor as d
                    d = d().decompress
                except:
                    return info(string.not_installed2 % 'LZMA')
                try:
                    data = d(data[:9] + bytes(4) + data[9:])
                except:
                    data = d(data[:5] + b'\xff' * 8 + data[9:])
                info(string.detected_comp % 'LZMA')
                

        except:
            info(string.try_error)

        data = io.BytesIO(data)
        print()

        while 1:
            
            temp = data.read(5)
            if temp == bytes(5):
                data = struct.pack("4s?B", b"XCOD", uselzham, picCount) + scdata.getvalue()
                if not to_memory:
                    with open(f"{folder_export}{CurrentSubPath}{baseName.rstrip('_')}.xcod", "wb") as xc:
                        xc.write(data)
                    data = None
                
                return pngs, data

            fileType, fileSize, subType, width, height = struct.unpack("<BIBHH", temp + data.read(5))
            pixelSize = pixelsize(subType)


            baseName = os.path.basename(fileName)[::-1].split('.', 1)[1][::-1] + '_' * picCount
            info(string.about_sc % (baseName, fileType, fileSize, subType, width, height))

            img = Image.new(format(subType), (width, height))
            pixels = []

            bytes2rgba(data, subType, img, pixels)
            
            print()
            
            if fileType in (27, 28):
                join_image(img, pixels)
                print()
                
            if to_memory:
                pngs.append(img)
            else:
                info(string.png_save)

                img.save(f"{folder_export}{CurrentSubPath}{baseName}.png")
                info(string.saved)
            picCount += 1
            scdata.write(struct.pack(">BBHH", fileType, subType, width, height))
            print()


def compileSC(_dir, from_memory = [], imgdata = None, folder_export = None):
    name = _dir.split('/')[-2]
    if from_memory:
        files = from_memory
    else:
        files = []
        [files.append(i) if i.endswith(".png") else None for i in os.listdir(_dir)]
        files.sort()
        if not files:
            return info(string.dir_empty % _dir.split('/')[-2])
        files = [Image.open(f'{_dir}{i}') for i in files]

    exe = False
    info(string.collecting_inf)
    sc = io.BytesIO()
    
    if from_memory:
        uselzham = imgdata['uselzham']
    else:
        try:
            scdata = open(f"{_dir}{name}.xcod", "rb")
            scdata.read(4)
            uselzham, = struct.unpack("?", scdata.read(1))
            scdata.read(1)
            hasxcod = True
        except:
            info(string.not_xcod)
            info(string.standart_types)
            hasxcod = False
            uselzham = False
        

    if uselzham:
        try:
           import lzham
        except:
            if not isWin:
                return info(string.not_installed2 % 'LZHAM')
            exe = True
    else:
        try:
            import lzma
        except:
            if not isWin:
                return info(string.not_installed2 % 'LZMA')
            exe = True
        
    for picCount in range(len(files)):
        print()
        img = files[picCount]
        
        if from_memory:
            fileType = imgdata['data'][picCount]['fileType']
            subType = imgdata['data'][picCount]['subType']
        else:
            if hasxcod:
                fileType, subType, width, height = struct.unpack(">BBHH", scdata.read(6))

                if (width, height) != img.size:
                    info(string.illegal_size % (width, height, img.width, img.height))
                    if question(string.resize_qu):
                        info(string.resizing)
                        img = img.resize((width, height), Image.ANTIALIAS)
            else:
                fileType, subType = 1, 0

        width, height = img.size
        pixelSize = pixelsize(subType)
        img = img.convert(format(subType))

        fileSize = width * height * pixelSize + 5

        info(string.about_sc % (name + '_' * picCount, fileType, fileSize, subType, width, height))

        sc.write(struct.pack("<BIBHH", fileType, fileSize, subType, width, height))

        if fileType in (27, 28):
            split_image(img)
            print()

        rgba2bytes(sc, img, subType)
        print()

    sc.write(bytes(5))
    sc = sc.getvalue()
    print()
    with open(f"{folder_export}{name}.sc", "wb") as fout:
        fout.write(struct.pack(">2sII16s", b'SC', 1, 16, hashlib.md5(sc).digest()))
        info(string.header_done)
        if uselzham:
            info(string.comp_with % 'LZHAM')
            fout.write(struct.pack("<4sBI", b'SCLZ', 18, len(sc)))
            if exe:
                with open('temp.sc', 'wb') as s:
                    s.write(sc)
                if os.system(f'{lzham_path} -d18 -c c temp.sc _temp.sc{nul}'):
                    raise Exception(string.comp_err)
                with open('_temp.sc', 'rb') as s:
                    s.read(13)
                    compressed = s.read()
                [os.remove(i) for i in ('temp.sc', '_temp.sc')]

            else:
                compressed = lzham.compress(sc, {"dict_size_log2": 18})

            fout.write(compressed)
        else:
            info(string.comp_with % 'LZMA')
            l = struct.pack("<I", len(sc))
            sc = lzma.compress(sc, format=lzma.FORMAT_ALONE, filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 0x40000, "lc": 3, "lp": 0, "pb": 2, "mode": lzma.MODE_NORMAL}])
            fout.write(sc[:5] + l + sc[13:])
        info(string.comp_done)
        print()

def decodeSC(fileName, sheetimage, check_lowres=True):
    fh = open(fileName, 'rb')
    start = fh.read(6)
    if start == b'SC\x00\x00\x00\x01':
        fh.read(20)
        start = b''
    data = start + fh.read()

    info(string.collecting_inf)

    try:
        uselzham = False
        if data[:4] == b'SCLZ':
            try:
                from lzham import decompress as d
                dict_size, data_size = struct.unpack("<BI", data[4:9])
                data = d(data[9:], data_size, {"dict_size_log2": dict_size})
            except:
                if not isWin:
                    return info(string.not_installed2 % 'LZHAM')
                with open('temp.sc', 'wb') as sc:
                    sc.write(b'LZH\x30' + data[4:9] + bytes(4) + data[9:])
                if os.system(f'{lzham_path} -d{data[4]} -c d temp.sc _temp.sc{nul}'):
                    raise Exception(string.decomp_err)
                data = open('_temp.sc', 'rb').read()
                [os.remove(i) for i in ('temp.sc', '_temp.sc')]
            info(string.detected_comp % 'LZHAM')
            uselzham = True
        else:
            try:
                from lzma import LZMADecompressor as d
                d = d().decompress
            except:
                return info(string.not_installed2 % 'LZMA')
            try:
                data = d(data[:9] + bytes(4) + data[9:])
            except:
                data = d(data[:5] + b'\xff' * 8 + data[9:])
            info(string.detected_comp % 'LZMA')
    except: pass

    reader = Reader(data)
    ldata = len(data)
    del data

    OffsetShape = 0
    OffsetSheet = 0

    class SheetData:
        def __init__(self):
            self.pos = (0, 0)

    class SpriteGlobals:
        def __init__(self):
            self.shape_count = 0
            self.total_animations = 0
            self.total_textures = 0
            self.text_field_count = 0
            self.matrix_count = 0
            self.color_transformation_count = 0
            self.export_count = 0

    class SpriteData:
        def __init__(self):
            self.id = 0
            self.total_regions = 0
            self.regions = []

    class Region:
        def __init__(self):
            self.sheet_id = 0
            self.num_points = 0
            self.rotation = 0
            self.mirroring = 0
            self.shape_points = []
            self.sheet_points = []
            self.top = -32767
            self.left = 32767
            self.bottom = 32767
            self.right = -32767
            self.size = (0, 0)

    class ShapePoint(SpriteData):
        pass

    class SheetPoint(SpriteData):
        pass

    spriteglobals = SpriteGlobals()

    spriteglobals.shape_count = reader.uint16
    spriteglobals.total_animations = reader.uint16
    spriteglobals.total_textures = reader.uint16
    spriteglobals.text_field_count = reader.uint16
    spriteglobals.matrix_count = reader.uint16
    spriteglobals.color_transformation_count = reader.uint16

    sheetdata = [SheetData() for x in range(spriteglobals.total_textures)]
    spritedata = [SpriteData() for x in range(spriteglobals.shape_count)]

    reader.uint32
    reader.byte

    spriteglobals.export_count = reader.uint16

    for i in range(spriteglobals.export_count):
        reader.uint16

    for i in range(spriteglobals.export_count):
        reader.string()

    while ldata - reader.stream.tell():

        DataBlockTag = '%02x' % reader.byte
        DataBlockSize = reader.uint32

        if DataBlockTag == "01" or DataBlockTag == "18":
            
            PixelType = reader.byte

            sheetdata[OffsetSheet].pos = (reader.uint16, reader.uint16)


            if check_lowres and sheetimage[OffsetSheet].size != sheetdata[OffsetSheet].pos:
                i = 2
            else:
                i = 1

            OffsetSheet += 1
            
            continue            
    

        if DataBlockTag == "1e":
            continue
        elif DataBlockTag == "1a":
            continue

        elif DataBlockTag == '00':
            continue

        elif DataBlockTag == "12":
            
            spritedata[OffsetShape].id = reader.uint16
            
            spritedata[OffsetShape].total_regions = reader.uint16
            TotalsPointCount = reader.uint16


            for y in range(spritedata[OffsetShape].total_regions):

                region = Region()

                DataBlockTag16 = '%02x' % reader.byte
                
                if DataBlockTag16 == "16":
                    DataBlockSize16 = reader.uint32
                    region.sheet_id = reader.byte
                    
                    region.num_points = reader.byte
                    
                    region.shape_points  = [ShapePoint() for z in range(region.num_points)]
                    region.sheet_points = [SheetPoint() for z in range(region.num_points)]

                    for z in range(region.num_points):
                        region.shape_points[z].pos = (reader.int32, reader.int32)
                    for z in range(region.num_points):
                        region.sheet_points[z].pos = (int(round(reader.uint16 * sheetdata[region.sheet_id].pos[0] / 65535) / i),
                                                    int(round(reader.uint16 * sheetdata[region.sheet_id].pos[1] / 65535) / i))

                spritedata[OffsetShape].regions.append(region)

            reader.uint32
            reader.byte

            OffsetShape += 1

            continue

        elif DataBlockTag == "08": #Matrix
            [reader.int32 for i in range(6)]
            continue
        elif DataBlockTag == "0c": #Animation
            reader.uint16
            reader.byte
            reader.uint16

            cnt1 = reader.int32

            for i in range(cnt1):
                reader.uint16
                reader.uint16
                reader.uint16

            cnt2 = reader.uint16

            for i in range(cnt2):
                reader.uint16

            for i in range(cnt2):
                reader.byte

            for i in range(cnt2):
                StringLength = reader.byte
                if StringLength < 255:
                    reader.stream.read(StringLength)
            continue

        else:
            reader.stream.read(DataBlockSize)
        
    maxLeft = 0
    maxRight = 0
    maxAbove = 0
    maxBelow = 0

    for x in range(spriteglobals.shape_count):
        for y in range(spritedata[x].total_regions):

            region = spritedata[x].regions[y]
            
            regionMinX = 32767
            regionMaxX = -32767
            regionMinY = 32767
            regionMaxY = -32767
            for z in range (region.num_points):
                tmpX, tmpY = region.shape_points[z].pos
                
                
                if tmpY > region.top:
                    region.top = tmpY
                if tmpX < region.left:
                    region.left = tmpX
                if tmpY < region.bottom:
                    region.bottom = tmpY
                if tmpX > region.right:
                    region.right = tmpX
                
                
                sheetpoint = region.sheet_points[z]

                tmpX, tmpY = sheetpoint.pos

                if tmpX < regionMinX:
                    regionMinX = tmpX
                if tmpX > regionMaxX:
                    regionMaxX = tmpX
                if tmpY < regionMinY:
                    regionMinY = tmpY
                if tmpY > regionMaxY:
                    regionMaxY = tmpY

            region = region_rotation(region)

            tmpX, tmpY = regionMaxX - regionMinX, regionMaxY - regionMinY
            size = (tmpX, tmpY)

            if region.rotation in (90, 270):
                size = size[::-1]

            region.size = size

        spritedata[x].regions[y] = region

    return spriteglobals, spritedata, sheetdata

    
def cut_sprites(spriteglobals, spritedata, sheetdata, sheetimage, xcod, folder_export):
    xcod.write(struct.pack('>H', spriteglobals.shape_count))

    for x in range(spriteglobals.shape_count):
        xcod.write(struct.pack('>H', spritedata[x].total_regions))

        progressbar(string.cut_sprites % (x+1, spriteglobals.shape_count), x, spriteglobals.shape_count)
            
        for y in range(spritedata[x].total_regions):
            
            region = spritedata[x].regions[y]

            polygon = [region.sheet_points[z].pos for z in range(region.num_points)]

            xcod.write(struct.pack('>2B2H', region.sheet_id, region.num_points, *sheetdata[region.sheet_id].pos) + b''.join(struct.pack('>2H', *i) for i in polygon) + struct.pack('?B', region.mirroring, region.rotation // 90))

        
            imMask = Image.new('L', sheetdata[region.sheet_id].pos, 0)
            ImageDraw.Draw(imMask).polygon(polygon, fill=255)
            bbox = imMask.getbbox()
            if not bbox:
                continue

            regionsize = (bbox[2] - bbox[0], bbox[3] - bbox[1])
            tmpRegion = Image.new('RGBA',  regionsize,  None)
                
            tmpRegion.paste(sheetimage[region.sheet_id].crop(bbox),  None,  imMask.crop(bbox))
            if region.mirroring:
                tmpRegion = tmpRegion.transform(regionsize, Image.EXTENT, (regionsize[0], 0, 0, regionsize[1]))
                
            tmpRegion.rotate(region.rotation, expand=True) \
            .save(f'{folder_export}/{x}_{y}.png')
    print()

def place_sprites(xcod, folder):
    xcod = open(xcod, 'rb')
    files = os.listdir(folder)

    xcod.read(4)
    uselzham, picCount = struct.unpack('2B', xcod.read(2))
    sheetimage = []
    sheetimage_data = {'uselzham': uselzham, 'data': []}
    for i in range(picCount):
        fileType, subType, width, height = struct.unpack(">BBHH", xcod.read(6))
        sheetimage.append(Image.new('RGBA', (width, height)))
        sheetimage_data['data'].append({'fileType': fileType, 'subType': subType})

    shape_count, = struct.unpack('>H', xcod.read(2))

    for x in range(shape_count):

        progressbar(string.place_sprites % (x+1, shape_count), x, shape_count)

        total_regions, = struct.unpack('>H', xcod.read(2))

        for y in range(total_regions):

            sheet_id, num_points, x1, y1 = struct.unpack('>2B2H', xcod.read(6))
            polygon = [struct.unpack('>2H', xcod.read(4)) for i in range(num_points)]
            mirroring, rotation = struct.unpack('?B', xcod.read(2))
            rotation *= 90

            if f'{x}_{y}.png' not in files:
                continue

            tmpRegion = Image.open(f'{folder}/{x}_{y}.png') \
            .convert('RGBA') \
            .rotate(360 - rotation, expand=True)

            imMask = Image.new('L', (x1, y1), 0)
            ImageDraw.Draw(imMask).polygon(polygon, fill=255)
            bbox = imMask.getbbox()
            if not bbox:
                continue

            regionsize = (bbox[2] - bbox[0], bbox[3] - bbox[1])

            if mirroring:
                tmpRegion = tmpRegion.transform(regionsize, Image.EXTENT, (tmpRegion.width, 0, 0, tmpRegion.height))

            sheetimage[sheet_id].paste(tmpRegion, bbox[:2],  tmpRegion)
    print()

    return sheetimage, sheetimage_data

def region_rotation(region):

    def calc_sum(points, z):
        x1, y1 = points[(z + 1) % num_points].pos
        x2, y2 = points[z].pos
        return (x1 - x2) * (y1 + y2)

    sumSheet = 0
    sumShape = 0
    num_points = region.num_points

    for z in range(num_points):
        sumSheet += calc_sum(region.sheet_points, z)
        sumShape += calc_sum(region.shape_points, z)
    
    sheetOrientation = -1 if (sumSheet < 0) else 1
    shapeOrientation = -1 if (sumShape < 0) else 1
    
    region.mirroring = 0 if (shapeOrientation == sheetOrientation) else 1
    
    if region.mirroring:
        for x in range(num_points):
            pos = region.shape_points[x].pos
            region.shape_points[x].pos = (pos[0] *- 1, pos[1])
    
    pos00 = region.sheet_points[0].pos 
    pos01 = region.sheet_points[1].pos 
    pos10 = region.shape_points[0].pos
    pos11 = region.shape_points[1].pos

    if pos01[0] > pos00[0]:
        px = 1
    elif pos01[0] < pos00[0]:
        px = 2
    else:
        px = 3

    if pos01[1] < pos00[1]:
        py = 1
    elif pos01[1] > pos00[1]:
        py = 2
    else:
        py = 3

    if pos11[0] > pos10[0]:
        qx = 1
    elif pos11[0] < pos10[0]:
        qx = 2
    else:
        qx = 3

    if pos11[1] > pos10[1]:
        qy = 1
    elif pos11[1] < pos10[1]:
        qy = 2
    else:
        qy = 3
    
    rotation = 0
    if px == qx and py == qy:
        rotation = 0

    elif px == 3:
        if px == qy:
            if py == qx :
                rotation = 1
            else:
                rotation = 3
        else:
            rotation = 2

    elif py == 3:
        if py == qx:
            if px == qy:
                rotation = 3
            else:
                rotation = 1
        else:
            rotation = 2

    elif px != qx and py != qy:
        rotation = 2

    elif px == py:
        if px != qx:
            rotation = 3
        elif py != qy:
            rotation = 1

    elif px != py:
        if px != qx:
            rotation = 1
        elif py != qy:
            rotation = 3

    if sheetOrientation == -1 and rotation in (1, 3):
        rotation += 2
        rotation %= 4
    
    region.rotation = rotation * 90
    return region

