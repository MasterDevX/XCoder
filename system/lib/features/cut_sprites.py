import os

from system.lib.console import Console
from system.lib.swf import SupercellSWF
from system.localization import locale


def cut_sprites(swf: SupercellSWF, export_folder: str):
    os.makedirs(f'{export_folder}/overwrite', exist_ok=True)
    os.makedirs(f'{export_folder}/shapes', exist_ok=True)

    shapes_count = len(swf.shapes)
    swf.xcod_writer.write_uint16(shapes_count)

    for shape_index in range(shapes_count):
        Console.progress_bar(
            locale.cut_sprites_process % (shape_index + 1, shapes_count),
            shape_index,
            shapes_count
        )

        shape = swf.shapes[shape_index]

        rendered_shape = shape.render(swf)
        rendered_shape.save(f'{export_folder}/shapes/{shape.id}.png')

        regions_count = len(shape.regions)
        swf.xcod_writer.write_uint16(shape.id)
        swf.xcod_writer.write_uint16(regions_count)
        for region_index in range(regions_count):
            region = shape.regions[region_index]

            swf.xcod_writer.write_ubyte(region.texture_index)
            swf.xcod_writer.write_ubyte(region.get_points_count())

            for i in range(region.get_points_count()):
                swf.xcod_writer.write_uint16(int(region.get_u(i)))
                swf.xcod_writer.write_uint16(int(region.get_v(i)))
            swf.xcod_writer.write_ubyte(1 if region.is_mirrored else 0)
            swf.xcod_writer.write_byte(region.rotation // 90)

            rendered_region = region.render(swf)
            rendered_region.save(f'{export_folder}/shape_{shape.id}_{region_index}.png')
