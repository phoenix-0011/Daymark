# Month calendar agenda update

## Behavior

- Mobile Month view uses a flat Sunday-to-Saturday calendar.
- The selected date is shown as an accent-colored circular day.
- Today keeps a subtle outline when it is not selected.
- Dates outside the active month are muted.
- Up to three task dots appear below each date.
- Tapping a date keeps Month view open and refreshes the inline agenda below it.
- Tapping a muted date from the adjacent month moves the calendar to that month and selects the date.
- The selected date is synchronized with Planner, so switching to Day later opens that same date.
- Tasks below the calendar retain edit, complete, and delete actions.
- Empty dates show a compact Add action.

## Rebuild

Do not remove `.buildozer` when a working cache exists.

```bash
./build_android.sh
./install_android.sh
```
