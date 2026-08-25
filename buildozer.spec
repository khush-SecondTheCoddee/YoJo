[app]
title = CBSE Class 10 Study Hub
package.name = cbseclass10notes
package.domain = org.cbsestudy
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Added openssl so requests/HTTPS endpoints work seamlessly
requirements = python3,kivy==2.3.0,requests,certifi,urllib3,charset-normalizer,idna,openssl

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Target only 64-bit ARM to avoid 32-bit NDK recipe linking failures
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
