[app]
title = Rocket Editor SFS
package.name = rockeditorsfs
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,txt
version = 1.0.0
requirements = python3,kivy,openssl,pyjnius,android
android.archs = arm64-v8a
android.minapi = 21
android.ndk = 23b
android.build_tools_version = 34.0.0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
