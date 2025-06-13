[app]

# Application configuration
title = Rocket Editor SFS
package.name = rockeditorsfs
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,txt
version = 1.0.0

# Requirements (updated)
requirements = python3==3.10.0,kivy==2.2.1,openssl,pyjnius,android

# Android configuration (modern syntax)
android.archs = arm64-v8a  # Multi-architecture support
android.minapi = 21        # Minimum Android API level
android.ndk = 23b          # NDK version
android.sdk_path =         # Leave empty for auto-detect
android.build_tools_version = 34.0.0  # Latest stable build-tools

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
