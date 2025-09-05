
import logging
from logging.handlers import RotatingFileHandler


class MyLog:
    __logger__ = None

    @staticmethod
    def get_logger() -> logging.Logger:
        if MyLog.__logger__ is None:
            MyLog.__init__logger()
        return MyLog.__logger__

    def __init__logger():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG) # 設定 logger 的級別
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = RotatingFileHandler(
            'app.log',
            maxBytes=1024*1024*5, # 5 MB
            backupCount=5,
            encoding='utf-8' # 建議加上編碼，避免中文亂碼
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        MyLog.__logger__ = logger