# Animation stability update

The previous animation system moved and faded live page widgets. On Android,
those widgets contain nested layouts and scroll areas, so rapid taps could leave
multiple geometry/effect animations active at the same time.

The replacement uses a serialized paint-only transition:

- The outgoing page is captured once as a snapshot.
- The destination page is laid out normally and never moved.
- A short 210 ms outgoing snapshot fade/translation reveals the destination.
- The transition overlay temporarily blocks page input.
- A second navigation request is ignored until the current transition finishes.
- Day/Week/Month selection is locked for the same short interval.
- Highlight indicators have a single animation owner; interrupted animations are
  stopped and disposed before a new one starts.
- Rotation, responsive-layout changes, and language-direction changes cancel and
  snap transitions safely.
- RTL motion remains mirrored for Persian.

This pattern avoids animating live scroll views and is closer to the serialized,
input-locked navigation transitions used in polished mobile applications.

## Rebuild

Keep `icon.png` beside `main.py`, then run:

```bash
rm -rf .buildozer deployment buildozer.spec pysidedeploy.spec
./build_android.sh
```

The APK is written to:

```text
dist-android/Daymark-debug-arm64-v8a.apk
```
