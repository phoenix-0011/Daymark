# Daymark fixes applied

## Previously applied
- Rebuilt compact responsive layouts for the task, planner, week, month, and history screens.
- Made Tasks and History search fields expand across the full phone width.
- Replaced font-dependent theme, empty-state, and restore symbols with painted vector glyphs.
- Reworked the planner toolbar into two rows on phones; enlarged Day/Week/Month and navigation controls.
- Prevented planner navigation buttons from keeping a stale pressed/hover state on touch devices.
- Replaced nested Week view scroll areas with one smooth scrolling surface.
- Added touch-scroller press delay and motion tuning to avoid accidental button activation while dragging.
- Prevented stale Week/Calendar widgets from briefly overlapping during rapid refreshes.
- Redesigned New/Edit Task as a compact no-window-scroll form that keeps all controls visible in portrait phone layouts.
- Added a vertically scrollable Month surface for short screens.
- Made completion/deletion persistence immediate instead of waiting for toast animations.
- Reduced refresh work to the visible page to improve responsiveness and avoid flicker.
- Preserved sent-reminder state when edits do not change reminder timing.
- Prevented duplicate recurring tasks when a completed occurrence is restored.
- Allowed long task notes to display more naturally in task details.
- Added regression tests for reminder preservation and recurring-task restoration.

## Latest fixes
- Removed the compact Task Details outer scroll container and moved the content into a bordered panel so the details sheet fits as a proper non-scrolling dialog on phone screens.
- Centered compact dialogs more reliably and widened them to use the phone width more naturally.
- Increased the day selector width so the day number is fully visible.
- Improved the moon/night icon drawing so it appears visually straighter and cleaner.
- Tuned touch scrolling further for popup lists and long scroll areas.
- Added popup sizing controls to custom select fields so short lists like Repeat and Reminder open at full height without inner scrolling.
- Kept longer lists like Day, Month, and Category scrollable with better touch behavior.
- Disabled sticky touch hover visuals on Android while keeping clear pressed feedback.
- Ensured glyph buttons repaint and clear focus immediately after release.
- Highlighted the full current-day area in the Week planner more accurately, including the add button and panel border.
- Wrapped the desktop sidebar category list in a scroll area for large category counts.
- Kept the Add Task button and other touch actions out of persistent focus states for smoother interaction.
