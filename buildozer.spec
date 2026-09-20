[app]

# (str) Title of your application
title = Atlas

# (str) Package name
package.name = atlas

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (nur notwendige Endungen)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source patterns to exclude (wichtig, um Test-Dateien wegzulassen)
source.exclude_patterns = license, lambda*, kivy/tests/*

# (str) Application versioning
version = 0.1

# (list) Application requirements (Schlank gehalten)
requirements = python3,kivy,requests,pyjnius

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, FOREGROUND_SERVICE, WAKE_LOCK

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True)
android.private_storage = True

# (list) List of Android architectures to build for
android.archs = arm64-v8a

# (bool) Enable Android auto backup
android.allow_backup = True

[buildozer]

# (int) Log level (2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
