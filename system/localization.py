import json
import os


class Locale:
    def __init__(self):
        self.xcoder_header = None
        self.detected_os = None
        self.installing = None
        self.update_downloading = None
        self.crt_workspace = None
        self.verifying = None
        self.installed = None
        self.update_done = None
        self.not_installed = None
        self.clear_qu = None
        self.done = None
        self.choice = None
        self.to_continue = None
        self.experimental = None

        self.sc_label = None
        self.decode_sc = None
        self.encode_sc = None
        self.decode_by_parts = None
        self.encode_by_parts = None
        self.overwrite_by_parts = None
        self.decode_sc_description = None
        self.encode_sc_description = None
        self.decode_by_parts_description = None
        self.encode_by_parts_description = None
        self.overwrite_by_parts_description = None

        self.csv_label = None
        self.decompress_csv = None
        self.compress_csv = None
        self.decompress_csv_description = None
        self.compress_csv_description = None

        self.other_features_label = None
        self.check_update = None
        self.check_for_outdated = None
        self.reinit = None
        self.change_lang = None
        self.clear_dirs = None
        self.toggle_update_auto_checking = None
        self.exit = None
        self.version = None
        self.reinit_description = None
        self.change_lang_description = None
        self.clean_dirs_description = None

        self.not_latest = None
        self.done_err = None
        self.got_error = None
        self.collecting_inf = None
        self.about_sc = None
        self.skip_not_installed = None
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
        self.cut_sprites_process = None
        self.place_sprites_process = None
        self.not_implemented = None
        self.want_exit = None
        self.dec_sc = None
        self.error = None

        # new
        self.e1sc1 = None
        self.cgl = None
        self.upd_av = None
        self.upd_qu = None
        self.upd = None
        self.upd_ck = None
        self.bkp = None
        self.stp = None
        self.pause = None

        self.enabled = None
        self.disabled = None

    def load_from(self, language: str):
        language_filepath = './system/languages/' + language + '.json'
        english_language_filepath = './system/languages/en-EU.json'

        loaded_locale = {}
        if os.path.exists(language_filepath):
            loaded_locale = json.load(open(language_filepath, encoding='utf-8'))  # Any
        english_locale = json.load(open(english_language_filepath))  # English

        for key in self.__dict__:
            if key in loaded_locale:
                setattr(self, key, loaded_locale[key])
                continue
            setattr(self, key, english_locale[key])
