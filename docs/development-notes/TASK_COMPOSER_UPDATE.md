# Mobile task composer update

This update replaces the compact Add/Edit Task form with a keyboard-aware mobile composer.

## Composer
- Large task title input.
- Inline editable subtasks with add/remove controls.
- Notes stay optional and collapsed until requested.
- Bottom toolbar: category, scheduling, add subtask, templates, save.
- Category selection stays above the keyboard; scheduling and templates dismiss the keyboard first.
- The sheet follows the Android input-method rectangle so it remains above the keyboard.

## Scheduling
- Custom month calendar.
- Today, Tomorrow, 3 days later, This Sunday, and No date shortcuts.
- Optional time, reminder, and recurrence controls.

## Templates
- Local English/Turkish template library grouped by Health, Life, Sports, Mind, and Habits.
- Searchable list.
- Editable title, category, subtasks, recurrence, and time before applying.
- Applying a template returns to the composer for final customization.

## Data
- New SQLite `subtasks` table with cascading deletion.
- Subtasks are saved, edited, searched, shown in details/task cards, and copied to recurring occurrences.
