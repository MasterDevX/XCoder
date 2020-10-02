import json
import os


class Locale:
    def __init__(self):
        self.xcoder = None
        self.detected_os = None
        self.installing = None
        self.crt_workspace = None
        self.verifying = None
        self.installed = None
        self.not_installed = None
        self.clear_qu = None
        self.done = None
        self.choice = None
        self.to_continue = None
        self.experimental = None
        self.sc = None
        self.dsc = None
        self.dsc_desc = None
        self.esc = None
        self.esc_desc = None
        self.d1sc = None
        self.e1sc = None
        self.oth = None
        self.check_update = None
        self.version = None
        self.reinit = None
        self.reinit_desc = None
        self.relang = None
        self.relang_desc = None
        self.clean_dirs = None
        self.clean_dirs_desc = None
        self.exit = None
        self.done_err = None
        self.got_error = None
        self.collecting_inf = None
        self.about_sc = None
        self.try_error = None
        self.not_installed2 = None
        self.decompression_error = None
        self.detected_comp = None
        self.unk_type = None
        self.crt_pic = None
        self.join_pic = None
        self.png_save = None
        self.saved = None
        self.not_xcod = None
        self.default_types = None
        self.illegal_size = None
        self.resize_qu = None
        self.resizing = None
        self.split_pic = None
        self.writing_pic = None
        self.header_done = None
        self.compressing_with = None
        self.compression_error = None
        self.compression_done = None
        self.dir_empty = None
        self.not_found = None
        self.cut_sprites = None
        self.place_sprites = None
        self.not_implemented = None
        self.want_exit = None
        self.dec_sc = None
        self.dec_sc_tex = None
        self.error = None

    def load_from(self, language: str):
        language_file_path = 'system/languages/' + language + '.json'
        english_language_file_path = 'system/languages/en-EU.json'

        loaded_locale = {}
        if os.path.exists(language_file_path):
            loaded_locale = json.load(open(language_file_path, encoding='utf-8'))  # Any
        english_locale = json.load(open(english_language_file_path))  # English

        for key in self.__dict__:
            if key in loaded_locale:
                setattr(self, key, loaded_locale[key])
                continue
            setattr(self, key, english_locale[key])


if __name__ == '__main__':
    locale = Locale()
    locale.load_from('ru-RU')

    print(locale.xcoder % '0.1')
