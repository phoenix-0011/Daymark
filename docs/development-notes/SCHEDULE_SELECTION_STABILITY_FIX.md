# Schedule selection stability fix

The Schedule Task page now has invariant geometry while selecting dates:

- six calendar week rows are always reserved;
- selecting a date updates button state in place;
- vertical scroll position is preserved;
- quick-date controls have an explicit gap below the calendar;
- Time, Reminder, and Repeat are isolated into vertically spaced mobile groups;
- selectors use explicit heights and bottom padding to prevent clipping.
