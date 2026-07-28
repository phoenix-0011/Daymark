# Mine / Insights update

This update adds a fourth navigation destination called **Mine** (Turkish: **Ben**) while preserving Tasks, Planner, and History.

The page is driven entirely by the existing Daymark database and includes:

- current completion streak
- completed, pending, overdue, and completion-rate metrics
- selectable annual completion heatmap
- all-time completion donut
- last-seven-days completion bars
- top completed-task categories
- scheduled-task outlook for the next seven days

All charts are custom Qt painting widgets, so the Android package does not need another charting dependency.
