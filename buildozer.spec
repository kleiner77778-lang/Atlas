[app]

# (str) Title of your application
title = Atlas E-Lkw Tracker

# (str) Package name
package.name = atlastracker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.atlas

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# pyjnius für GPS & openssl für HTTPS/Telegram
requirements = python3,kivy,requests,pyjnius,openssl,urllib3,chardet,certifi,idna

# (str) Custom application icon
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientations (portrait, landscape, sensorLandscape, all)
orientation = all

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, FOREGROUND_SERVICE, WAKE_LOCK, INTERNET

# (list) Features
android.features = android.hardware.location.gps

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip building the ndk recipes
android.skip_update = False

# (bool) If True, accept all SDK licences
android.accept_sdk_license = True

# (str) Nur für arm64-v8a bauen (spart Zeit und verhindert Build-Timeouts)
android.archs = arm64-v8a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1
