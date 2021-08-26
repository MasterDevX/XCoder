import json
import os


class Config:
    config_path = './system/config.json'
    inited: bool

    def __init__(self):
        self.config_items = (
            'initialized',
            'version',
            'lang',
            'has_update',
            'last_update',
            'auto_update',
        )

        self.initialized: bool = False
        self.version = None
        self.lang: str = 'en-EU'
        self.has_update: bool = False
        self.last_update: int = -1
        self.auto_update: bool = True

        self.load()

    def load(self):
        if os.path.isfile(self.config_path):
            for key, value in json.load(open(self.config_path)).items():
                setattr(self, key, value)

    def dump(self):
        json.dump({
            item: getattr(self, item)
            for item in self.config_items
        }, open(self.config_path, 'w'))


if __name__ == '__main__':
    config = Config()
    print(config.config_items)
