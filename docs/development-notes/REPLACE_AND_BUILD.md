# Replace and build

Replace the files included in the replacement archive, preserving the `daymark/` directory.

Your existing `icon.png` must remain next to `main.py`.

Then run:

```bash
cd /path/to/Daymark_Android_build_ready
rm -rf .buildozer deployment buildozer.spec pysidedeploy.spec
chmod +x build_android.sh
./build_android.sh
```

APK output:

```text
dist-android/Daymark-debug-arm64-v8a.apk
```

Install on an authorized USB device:

```bash
./install_android.sh
```
