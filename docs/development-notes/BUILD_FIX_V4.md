# Daymark Android build fix v4

This patch fixes:

- incorrect JDK 17 selection when Homebrew JDK 21 is installed;
- Buildozer 1.5.0 calling the legacy SDK manager despite the required SDK already being installed;
- incorrect rejection of python-for-android's normal `libpythonbin.so` launcher library.

The builder prints `Daymark Android builder v4` at startup so the installed version can be confirmed.
