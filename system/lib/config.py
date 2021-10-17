import json
import os


class Config:
    config_path = './system/config.json'
    inited: bool

    def __init__(self):
        self.config_items = (
            'initialized',
            'version',
            'language',
            'has_update',
            'last_update',
            'auto_update',
        )

        self.initialized: bool = False
        self.version = None
        self.language: str = 'en-EU'
        self.has_update: bool = False
        self.last_update: int = -1
        self.auto_update: bool = False

        self.load()

    def toggle_auto_update(self):
        self.auto_update = not self.auto_update
        self.dump()

    def change_language(self, language):
        self.language = language
        self.dump()

    def load(self):
        if os.path.isfile(self.config_path):
            for key, value in json.load(open(self.config_path)).items():
                setattr(self, key, value)

    def dump(self):
        json.dump({
            item: getattr(self, item)
            for item in self.config_items
        }, open(self.config_path, 'w'))


config = Config()
