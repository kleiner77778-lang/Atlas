[app]
title = Atlas TruckNavi
package.name = atlastrucknavi
package.domain = org.atlas
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.1
requirements = python3,kivy,urllib3,requests,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,VIBRATE,MODIFY_AUDIO_SETTINGS
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 31
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
