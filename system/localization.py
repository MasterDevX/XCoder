import json
import os
from typing import Optional


class Locale:
    def __init__(self):
        self.xcoder_header: Optional[str] = None
        self.detected_os: Optional[str] = None
        self.installing: Optional[str] = None
        self.update_downloading: Optional[str] = None
        self.crt_workspace: Optional[str] = None
        self.verifying: Optional[str] = None
        self.installed: Optional[str] = None
        self.update_done: Optional[str] = None
        self.not_installed: Optional[str] = None
        self.clear_qu: Optional[str] = None
        self.done: Optional[str] = None
        self.done_qu: Optional[str] = None
        self.choice: Optional[str] = None
        self.to_continue: Optional[str] = None
        self.experimental: Optional[str] = None

        self.sc_label: Optional[str] = None
        self.decode_sc: Optional[str] = None
        self.encode_sc: Optional[str] = None
        self.decode_by_parts: Optional[str] = None
        self.encode_by_parts: Optional[str] = None
        self.overwrite_by_parts: Optional[str] = None
        self.decode_sc_description: Optional[str] = None
        self.encode_sc_description: Optional[str] = None
        self.decode_by_parts_description: Optional[str] = None
        self.encode_by_parts_description: Optional[str] = None
        self.overwrite_by_parts_description: Optional[str] = None

        self.csv_label: Optional[str] = None
        self.decompress_csv: Optional[str] = None
        self.compress_csv: Optional[str] = None
        self.decompress_csv_description: Optional[str] = None
        self.compress_csv_description: Optional[str] = None

        self.other_features_label: Optional[str] = None
        self.check_update: Optional[str] = None
        self.check_for_outdated: Optional[str] = None
        self.reinit: Optional[str] = None
        self.change_language: Optional[str] = None
        self.clear_directories: Optional[str] = None
        self.toggle_update_auto_checking: Optional[str] = None
        self.exit: Optional[str] = None
        self.version: Optional[str] = None
        self.reinit_description: Optional[str] = None
        self.change_lang_description: Optional[str] = None
        self.clean_dirs_description: Optional[str] = None

        self.not_latest: Optional[str] = None
        self.collecting_inf: Optional[str] = None
        self.about_sc: Optional[str] = None
        self.skip_not_installed: Optional[str] = None
        self.decompression_error: Optional[str] = None
        self.detected_comp: Optional[str] = None
        self.unk_type: Optional[str] = None
        self.crt_pic: Optional[str] = None
        self.join_pic: Optional[str] = None
        self.png_save: Optional[str] = None
        self.saved: Optional[str] = None
        self.xcod_not_found: Optional[str] = None
        self.illegal_size: Optional[str] = None
        self.resize_qu: Optional[str] = None
        self.resizing: Optional[str] = None
        self.split_pic: Optional[str] = None
        self.writing_pic: Optional[str] = None
        self.header_done: Optional[str] = None
        self.compressing_with: Optional[str] = None
        self.compression_error: Optional[str] = None
        self.compression_done: Optional[str] = None
        self.dir_empty: Optional[str] = None
        self.not_found: Optional[str] = None
        self.cut_sprites_process: Optional[str] = None
        self.place_sprites_process: Optional[str] = None
        self.not_implemented: Optional[str] = None
        self.error: Optional[str] = None

        # new
        self.e1sc1: Optional[str] = None
        self.cgl: Optional[str] = None
        self.upd_av: Optional[str] = None
        self.upd_qu: Optional[str] = None
        self.upd: Optional[str] = None
        self.upd_ck: Optional[str] = None
        self.bkp: Optional[str] = None
        self.stp: Optional[str] = None

        self.enabled: Optional[str] = None
        self.disabled: Optional[str] = None

        self.install_to_unlock: Optional[str] = None

    def load(self, language: str):
        language_filepath = "./system/languages/" + language + ".json"
        english_language_filepath = "./system/languages/en-EU.json"

        loaded_locale = {}
        if os.path.exists(language_filepath):
            loaded_locale = json.load(open(language_filepath, encoding="utf-8"))  # Any
        english_locale = json.load(open(english_language_filepath))  # English

        for key in self.__dict__:
            if key in loaded_locale:
                setattr(self, key, loaded_locale[key])
                continue
            setattr(self, key, english_locale[key])

    def change(self):
        language_files = os.listdir("./system/languages/")

        print("Select Language\nВыберите язык\nВиберіть Мову\n")

        for file_index in range(len(language_files)):
            language_path = "./system/languages/" + language_files[file_index]
            language_name = json.load(open(language_path, encoding="utf-8"))["name"]

            print(f"{file_index + 1} - {language_name}")

        language_index = input("\n>>> ")
        try:
            language_index = int(language_index) - 1
            if language_index >= 0:
                if language_index < len(language_files):
                    language = ".".join(language_files[language_index].split(".")[:-1])
                    self.load(language)

                    return language
        except ValueError:
            pass

        return self.change()


locale = Locale()
