# Compact Task Composer Fix

This update addresses the Android task-composer layout issues reported on Samsung devices.

## Changes

- Suppresses detached Android text-selection handles with `Qt.ImhNoTextHandles`.
- Clears editor focus, selections, and the input method before closing any managed dialog.
- Replaces the full-height task composer with a compact, top-anchored sheet.
- Keeps the composer entirely above the visible keyboard.
- Keeps title, notes, schedule summary, and toolbar in deterministic vertical order.
- Uses a dedicated subtask scroll area:
  - expands for the first few rows;
  - scrolls only when subtasks become numerous;
  - grows and shrinks when rows are added or removed.
- Keeps Notes immediately below the subtask region.
- Opening Notes no longer automatically focuses the editor or creates an early native cursor handle.
- Prevents a full-screen flash before the compact geometry is applied.

## Files changed

- `daymark/dialogs.py`
- `daymark/theme.py`
