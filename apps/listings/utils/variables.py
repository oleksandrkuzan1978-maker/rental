from datetime import time

DEFAULT_CHECK_IN_TIME = time(hour=14, minute=0)  # час начала срока бронирования
DEFAULT_CHECK_OUT_TIME = time(hour=11, minute=0) # час окончания срока бронирования

MAX_ROOMS = 20 # Максимально возможное кол-во комнат

MAX_FILES_PER_LISTING = 7 # Максимальное количество файлов (картинок) объявления