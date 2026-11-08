"""Проверки расширения и размера файлов, выбор свободного пути и запись в MEDIA_ROOT."""

import os
# from pathlib import Path
# from django.conf import settings
# from uuid import uuid4

#ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "pdf"]


# # Функция на проверку валидных расширений файла
# def check_extension(filename):
#     """Вернуть True, если последнее расширение имени входит в ALLOWED_EXTENSIONS.
#
#     Сравнение чувствительно к регистру: .PDF и .pdf считаются разными расширениями.
#     """
#     extension = Path(filename).suffix.lower()
#     if extension not in ALLOWED_EXTENSIONS:
#         return False
#     return True


# # ● Функция на проверку размерности файла (файл не должен быть больше 2 MB)
# def check_file_size(file, required_size=2):
#     # Переводим в Мегабайты
#     """Проверить, что file.size не превышает required_size МиБ (по умолчанию 2).
#
#     Граничный размер разрешён; file должен предоставлять размер в байтах через атрибут size.
#     """
#     file_size = file.size / (1024 * 1024)
#     if file_size > required_size:
#         return False
#     return True

# def property_file_upload_to(instance, filename):
#     extension = Path(filename).suffix.lower()
#     return (
#         f"users/{instance.property.user_id}/"
#         f"properties/{instance.property_id}/"
#         f"{uuid4().hex}{extension}"
#     )

# def save_file(file_path, file_content):
#     # Извлекаем путь к папке (documents/) и создаем её, если она еще не существует
#     # file_path — относительный путь, например documents/report.pdf
#     # directory = os.path.dirname(file_path)
#     """Записать file_content порциями по пути MEDIA_ROOT / file_path и вернуть file_path.
#
#     Ожидает относительный путь и объект с методом chunks(). Создаёт родительские папки,
#     а существующий файл с тем же путём перезаписывает.
#     """
#     full_path = Path(settings.MEDIA_ROOT) / file_path
#     directory = os.path.dirname(full_path)
#     if directory:
#         os.makedirs(directory, exist_ok=True)
#
#     # Открываем файл на запись в бинарном режиме ('wb')
#     with open(full_path, 'wb') as f:
#         # Метод .chunks() читает файл порциями, избегая перегрузки оперативной памяти
#         for chunk in file_content.chunks():
#             f.write(chunk)
#
#     return file_path

# # ● Функция на создание пути для сохранения файла
# def create_file_path(file_name):
#     """Выбрать свободный относительный путь documents/<имя>.<расширение> внутри MEDIA_ROOT.
#
#     Разделяет имя по последней точке; при совпадении добавляет суффиксы _1, _2 и далее.
#     Имя должно содержать точку. Файл не создаёт и путь не резервирует, поэтому одновременные
#     вызовы могут выбрать одинаковый путь.
#     """
#     new_file_name, file_ext = file_name.rsplit('.', 1)
#
#     file_path = "documents/{}.{}".format(
#         new_file_name,
#         file_ext,
#     )
#
#     counter = 1
#
#     while (settings.MEDIA_ROOT / file_path).exists():
#         file_path = "documents/{}_{}.{}".format(
#             new_file_name,
#             counter,
#             file_ext,
#         )
#         counter += 1
#
#     return file_path


# ● Функция на сохранение файла (файл должен записываться по частям для избежания
# потенциальных ошибок и потери данных)


