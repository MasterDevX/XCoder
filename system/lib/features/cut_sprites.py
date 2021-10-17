import os

from system.lib.console import Console
from system.lib.swf import SupercellSWF
from system.localization import locale


def cut_sprites(swf: SupercellSWF, folder_export):
    os.makedirs(f'{folder_export}/overwrite', exist_ok=True)
    os.makedirs(f'{folder_export}/shapes', exist_ok=True)

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
        rendered_shape.save(f'{folder_export}/shapes/{shape.id}.png')

        regions_count = len(shape.regions)
        swf.xcod_writer.write_uint16(shape.id)
        swf.xcod_writer.write_uint16(regions_count)
        for region_index in range(regions_count):
            region = shape.regions[region_index]

            swf.xcod_writer.write_ubyte(region.texture_id)
            swf.xcod_writer.write_ubyte(region.points_count)

            for point in region.sheet_points:
                swf.xcod_writer.write_uint16(int(point.x))
                swf.xcod_writer.write_uint16(int(point.y))
            swf.xcod_writer.write_ubyte(1 if region.mirroring else 0)
            swf.xcod_writer.write_ubyte(region.rotation // 90)

            rendered_region = region.render(swf)
            rendered_region.save(f'{folder_export}/shape_{shape.id}_{region_index}.png')
    print()
