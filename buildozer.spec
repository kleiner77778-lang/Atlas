[app]
title = Atlas E-Lkw Tracker
package.name = elkwtracker
package.domain = org.elkw
source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 0.1
requirements = python3,kivy,requests,urllib3
orientation = portrait
android.permissions = INTERNET,ACCESS_FINE_LOCATION
android.api = 33
android.accept_sdk_license = True
android.minapi = 21
android.archs = arm64-v8a

[buildozer]
log_level = 1
warn_on_root = 1
