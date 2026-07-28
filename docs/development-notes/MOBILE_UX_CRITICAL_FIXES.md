# Daymark mobile UX critical fixes

This update coordinates dialogs, keyboard geometry, Android Back, page transitions,
swipe cards, scrolling, templates, and Month agenda refreshes through shared UI
controllers instead of isolated per-screen patches.

## Applied fixes

- Template library and template customization use managed full-page transitions.
- Template customization has a persistent Back button.
- New Task opens focused and requests the Android keyboard automatically.
- Editable pages resize above the keyboard and keep the focused field visible.
- All managed pages occupy the area below the persistent language/theme header.
- Android Back closes the active dialog, returns to Tasks, or exits once; repeated
  key events are consumed.
- New Task and all full-page editors have explicit Back/Close controls.
- Swipe actions remain hidden while closed and use aligned rounded action buttons.
- Touch scrolling uses one gesture recognizer per viewport with lighter physics.
- Main tabs use a short stable fade; Planner modes use a restrained directional
  transition. Transitions are serialized and task swipe state closes first.
- Month task saves refresh on the next event-loop turn to avoid re-entrant widget
  deletion on Android.
- Task Edit uses a dedicated vector Repeat icon.
- Recurrence metadata uses a vector icon rather than an unsupported Unicode glyph.
- Task Details is now a scrollable managed page.

## Play Protect note

A debug APK installed outside Google Play can still display a Play Protect warning.
That warning cannot be disabled from the app UI. For public or tester distribution,
build a release-signed artifact and distribute it through Google Play Internal
Testing or Internal App Sharing.
