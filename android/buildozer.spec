[app]

# (str) Title of your application
title = Flappy Bird

# (str) Package name
package.name = flappybird

# (str) Package domain (needs to be unique, like com.example.myapp)
package.domain = com.clyde

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,wav,ogg,ttf,ico

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy,pillow

# App icon (512x512 PNG, generated from assets/app.ico)
icon.filename = %(source.dir)s/assets/icon.png

# Splash screen while the app loads on device
presplash.filename = %(source.dir)s/assets/presplash.png
presplash.color = #384858

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 1

#
# Android specific
#

# (list) Permissions (audio playback does not require INTERNET)
android.permissions =

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 29

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) Indicate whether the screen should stay on
android.wakelock = True

# (str) The format used to package the app for debug mode (apk or aab).
android.debug_artifact = apk

# Auto-accept SDK licenses (needed for unattended builds)
android.accept_sdk_license = True


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
