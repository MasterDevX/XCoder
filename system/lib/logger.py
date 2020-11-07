import os
import time

from system.localization import Locale


class Logger:
    def __init__(self, language: str):
        self.locale = Locale()
        self.locale.load_from(language)

    def write(self, error: Exception):
        current_date = time.strftime('%d.%m.%Y %H:%M:%S')
        path = 'log.txt'
        if not os.path.isfile(path):
            mode = 'w'
        else:
            mode = 'a'
        log = open(path, mode, encoding='utf-8')
        log.write(self.locale.got_error % (current_date, error))
        log.close()
