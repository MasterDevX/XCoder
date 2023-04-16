import json
import os

DEFAULT_STRING = "NO LOCALE"


class Locale:
    def __init__(self):
        self.xcoder_header: str = DEFAULT_STRING
        self.detected_os: str = DEFAULT_STRING
        self.installing: str = DEFAULT_STRING
        self.update_downloading: str = DEFAULT_STRING
        self.crt_workspace: str = DEFAULT_STRING
        self.verifying: str = DEFAULT_STRING
        self.installed: str = DEFAULT_STRING
        self.update_done: str = DEFAULT_STRING
        self.not_installed: str = DEFAULT_STRING
        self.clear_qu: str = DEFAULT_STRING
        self.done: str = DEFAULT_STRING
        self.done_qu: str = DEFAULT_STRING
        self.choice: str = DEFAULT_STRING
        self.to_continue: str = DEFAULT_STRING
        self.experimental: str = DEFAULT_STRING

        self.sc_label: str = DEFAULT_STRING
        self.decode_sc: str = DEFAULT_STRING
        self.encode_sc: str = DEFAULT_STRING
        self.decode_by_parts: str = DEFAULT_STRING
        self.encode_by_parts: str = DEFAULT_STRING
        self.overwrite_by_parts: str = DEFAULT_STRING
        self.decode_sc_description: str = DEFAULT_STRING
        self.encode_sc_description: str = DEFAULT_STRING
        self.decode_by_parts_description: str = DEFAULT_STRING
        self.encode_by_parts_description: str = DEFAULT_STRING
        self.overwrite_by_parts_description: str = DEFAULT_STRING

        self.csv_label: str = DEFAULT_STRING
        self.decompress_csv: str = DEFAULT_STRING
        self.compress_csv: str = DEFAULT_STRING
        self.decompress_csv_description: str = DEFAULT_STRING
        self.compress_csv_description: str = DEFAULT_STRING

        self.other_features_label: str = DEFAULT_STRING
        self.check_update: str = DEFAULT_STRING
        self.check_for_outdated: str = DEFAULT_STRING
        self.reinit: str = DEFAULT_STRING
        self.change_language: str = DEFAULT_STRING
        self.clear_directories: str = DEFAULT_STRING
        self.toggle_update_auto_checking: str = DEFAULT_STRING
        self.exit: str = DEFAULT_STRING
        self.version: str = DEFAULT_STRING
        self.reinit_description: str = DEFAULT_STRING
        self.change_lang_description: str = DEFAULT_STRING
        self.clean_dirs_description: str = DEFAULT_STRING

        self.not_latest: str = DEFAULT_STRING
        self.collecting_inf: str = DEFAULT_STRING
        self.about_sc: str = DEFAULT_STRING
        self.skip_not_installed: str = DEFAULT_STRING
        self.decompression_error: str = DEFAULT_STRING
        self.detected_comp: str = DEFAULT_STRING
        self.unknown_pixel_type: str = DEFAULT_STRING
        self.crt_pic: str = DEFAULT_STRING
        self.join_pic: str = DEFAULT_STRING
        self.png_save: str = DEFAULT_STRING
        self.saved: str = DEFAULT_STRING
        self.xcod_not_found: str = DEFAULT_STRING
        self.illegal_size: str = DEFAULT_STRING
        self.resize_qu: str = DEFAULT_STRING
        self.resizing: str = DEFAULT_STRING
        self.split_pic: str = DEFAULT_STRING
        self.writing_pic: str = DEFAULT_STRING
        self.header_done: str = DEFAULT_STRING
        self.compressing_with: str = DEFAULT_STRING
        self.compression_error: str = DEFAULT_STRING
        self.compression_done: str = DEFAULT_STRING
        self.dir_empty: str = DEFAULT_STRING
        self.not_found: str = DEFAULT_STRING
        self.cut_sprites_process: str = DEFAULT_STRING
        self.place_sprites_process: str = DEFAULT_STRING
        self.not_implemented: str = DEFAULT_STRING
        self.error: str = DEFAULT_STRING

        # new
        self.e1sc1: str = DEFAULT_STRING
        self.cgl: str = DEFAULT_STRING
        self.upd_av: str = DEFAULT_STRING
        self.upd_qu: str = DEFAULT_STRING
        self.upd: str = DEFAULT_STRING
        self.upd_ck: str = DEFAULT_STRING
        self.bkp: str = DEFAULT_STRING
        self.stp: str = DEFAULT_STRING

        self.enabled: str = DEFAULT_STRING
        self.disabled: str = DEFAULT_STRING

        self.install_to_unlock: str = DEFAULT_STRING

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
