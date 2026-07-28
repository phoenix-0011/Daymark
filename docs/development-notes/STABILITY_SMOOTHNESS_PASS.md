# Daymark stability and smoothness pass

- Coalesces duplicate full-view refreshes into one frame-aligned refresh.
- Coalesces resize, keyboard, and dialog geometry signals.
- Avoids full-screen page snapshot animations on Android.
- Uses position-only swipe animation and lighter Android removal animation.
- Tunes Android kinetic scrolling for 60 FPS where supported and locks vertical pages to one axis.
- Removes nested `QApplication.processEvents()` from the composer.
- Defers Schedule/Templates until the keyboard hide request reaches the event loop.
- Stops rebuilding hidden planner modes during language changes.
- Prevents repeated same-width Schedule layout fitting.
- Debounces template and task searches.
- Updates task dates directly without rewriting subtasks.
- Makes database shutdown idempotent and adds bounded SQLite cache/journal pragmas.
- Adds a persistent `daymark-crash.log` for uncaught Python exceptions.
- Makes template rebuilds and child-dialog guards exception-safe.
- Prevents accidental horizontal kinetic movement in dropdowns and text editors.
- Removes the delayed composer geometry nudge after opening.
- Uses a lightweight timer-driven feedback toast on Android instead of a large graphics effect.
