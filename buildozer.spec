[app]

# Required fields
title = Rocket Editor SFS
package.name = rockeditorsfs
package.domain = org.example
version = 1.0.0  # <-- This was missing

# Build configuration
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,txt

# Requirements
requirements = python3,kivy,openssl,pyjnius,android

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
