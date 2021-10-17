import struct

from loguru import logger
from sc_compression import decompress, compress
from sc_compression.signatures import Signatures

from system.localization import locale


def write_sc(output_filename: str, buffer: bytes, use_lzham: bool):
    with open(output_filename, 'wb') as file_out:
        logger.info(locale.header_done)

        if use_lzham:
            logger.info(locale.compressing_with % 'LZHAM')
            file_out.write(struct.pack('<4sBI', b'SCLZ', 18, len(buffer)))
            compressed = compress(buffer, Signatures.SCLZ)

            file_out.write(compressed)
        else:
            logger.info(locale.compressing_with % 'LZMA')
            compressed = compress(buffer, Signatures.SC, 3)
            file_out.write(compressed)
        logger.info(locale.compression_done)


def open_sc(input_filename: str):
    decompressed = None
    use_lzham = False

    logger.info(locale.collecting_inf)
    with open(input_filename, 'rb') as f:
        filedata = f.read()
        f.close()

    try:
        decompressed, signature = decompress(filedata)
        #
        # logger.info(locale.detected_comp % signature.upper())
        #
        if signature == Signatures.SCLZ:
            use_lzham = True
    except TypeError:
        logger.info(locale.decompression_error)
        exit(1)

    return decompressed, use_lzham
