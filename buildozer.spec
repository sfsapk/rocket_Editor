[app]

# Название вашего приложения
title = Rocket Editor SFS

# Имя пакета (должно быть уникальным)
package.name = rockeditorsfs

# Домен (обычно используется com.example)
package.domain = org.example

# Путь к основному файлу Python
source.dir = .

# Главный файл Python
source.include_exts = py,png,jpg,jpeg,json,txt

# Версия приложения
version = 1.0.0

# Требования
requirements = python3,kivy,openssl,pyjnius,android

# Разрешения Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Минимальная версия Android API
android.api = 29

# Версия SDK
android.sdk = 28

# Версия NDK
android.ndk = 23b

# Архитектура
android.arch = arm64-v8a

# Копирование дополнительных файлов и папок
source.include_patterns = Details/*,Details_Output/*,icons/*,backgrounds/*

# Иконка приложения (должна быть в корне проекта)
icon.filename = %(source.dir)s/icons/icon.png

# Ориентация экрана
orientation = portrait

# Полный экран
fullscreen = 0

# Жесткая клавиатура (отключаем системную)
android.soft_input_mode = adjustResize

# Дополнительные настройки
android.allow_backup = True
android.meta_data = android.app.uses_cleartext_traffic=true
