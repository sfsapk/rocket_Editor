[app]

# Required fields
title = Rocket Editor SFS
package.name = rockeditorsfs
package.domain = org.example
version = 1.0.0  # <-- This was missing
# Python-for-android configuration
p4a.bootstrap = sdl2
p4a.ignore_setup_py = True
p4a.release_artifact = False

# NDK configuration
android.ndk_path = 
android.ndk_version = 23b
# Build configuration
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,txt

# Requirements
requirements = python3,kivy,openssl,pyjnius,android
requirements = python-for-android==2023.10.06, ...
# Android configuration
android.archs = arm64-v8a
android.minapi = 21
android.ndk = 23b
android.build_tools_version = 34.0.0
android.ant_path = /usr/bin/ant  # Use system Ant
android.skip_update = True  # Skip automatic updates

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Additional files
source.include_patterns = Details/*,Details_Output/*,icons/*,backgrounds/*

# App icon
icon.filename = %(source.dir)s/icons/icon.png

# Orientation
orientation = portrait
fullscreen = 0

# Input settings
android.soft_input_mode = adjustResize

# Metadata
android.allow_backup = True
android.meta_data = android.app.uses_cleartext_traffic=true
