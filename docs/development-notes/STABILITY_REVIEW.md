# Daymark stability and smoothness review

This update is based on the English/Turkish task-interactions build.

## Stability fixes

- Wrapped task, category, recurrence, star, date, restore, and reminder writes in safer UI error boundaries so a database error is shown to the user instead of terminating the Android process.
- Converted multi-step SQLite changes to transactions.
- Added SQLite busy timeout, WAL tuning, indexes, passive checkpointing, and `PRAGMA optimize`.
- Added a durable `generated_from_id` marker for recurring occurrences.
- Restoring a recurring task now removes its generated occurrence without deleting an independently-created identical task.
- New recurring occurrences reset their subtasks to incomplete.
- Repeated completion of the same task is idempotent.
- Updating a missing task rolls back instead of leaving partial subtask data.
- Removed inactive Persian/Jalali runtime branches from date controls and formatting.

## Gesture fixes

- Improved axis locking for kinetic scrolling.
- Vertical scrolling that begins on a task closes an exposed swipe row and does not trigger task editing.
- Swipe open/close uses velocity plus distance thresholds and keeps only one row open.
- Swipe action callbacks wait until the row has closed.
- Popup selection ignores duplicate Qt click/activation signals.

## Animation fixes

- One stack transition owns the screen at a time.
- Rapid navigation taps are coalesced to the latest destination.
- Pending destinations are not rebuilt twice while another transition is running.
- Stack transitions paint only the outgoing snapshot over a live destination page.
- Null snapshots fall back to an immediate safe switch.
- Cancelled transitions release their pixmaps.
- Highlight, swipe, and removal animations stop and dispose previous animation objects before starting another.

## Smoothness and performance

- Search updates are debounced and pending timers are cancelled before external refreshes.
- Visible list scroll positions are preserved during same-filter refreshes.
- Only the visible main page is refreshed after a task operation.
- Category controls are rebuilt only when category metadata or counts actually change.
- Android build v6 preserves the expensive `.buildozer` compiler cache by default.
- Use `DAYMARK_CLEAN_BUILD=1 ./build_android.sh` only when a true clean rebuild is required.

## Validation

- 20 automated tests pass.
- All Python source files compile successfully.
- Android shell scripts pass `bash -n` validation.
- A 500-task/1,000-subtask database stress read completed successfully in the local validation environment.

Final touch and frame pacing still require confirmation on the physical Android device.
