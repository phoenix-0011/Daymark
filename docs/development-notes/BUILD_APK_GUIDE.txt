DAYMARK ANDROID APK BUILD GUIDE
===============================

This package uses the Android configuration that previously built successfully:
- Python 3.11
- PySide6/Shiboken6 6.11.1 Android aarch64 wheels
- Android API 36
- Build Tools 36.0.0
- NDK 27.2.12479018
- plugins = platforms_qtforandroid
- local_libs left empty
- SDK and NDK passed explicitly to pyside6-android-deploy

1. Copy your existing icon.png into this project, beside main.py.
   It must be square and at least 512x512.

2. Open Terminal and enter this project directory:

   cd /path/to/Daymark_Android_export_ready

3. Make the scripts executable:

   chmod +x build_android.sh install_android.sh capture_android_log.sh

4. Build:

   ./build_android.sh

5. The APK will be created at:

   dist-android/Daymark-debug-arm64-v8a.apk

6. To install on the connected Android phone:

   ./install_android.sh

7. If the app installs but crashes after launch:

   ./capture_android_log.sh

   Then inspect or share:
   dist-android/daymark-logcat.txt
   dist-android/build.log

Do not rerun setup_android_toolchain.sh if your SDK/NDK are already working.
The build script automatically reuses:
- ~/.pyside6_android_deploy/android-sdk
- ~/.pyside6_android_deploy/android-ndk/AndroidNDK12479018.app/Contents/NDK
