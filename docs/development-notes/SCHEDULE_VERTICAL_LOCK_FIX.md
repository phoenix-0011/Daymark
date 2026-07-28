# Schedule dialog horizontal-scroll lock

This update removes horizontal movement from the Schedule Task page at every layer:

- a vertical-only QScrollArea subclass discards horizontal scroll deltas;
- the horizontal scrollbar range and value are permanently clamped to zero;
- QScroller horizontal overshoot is disabled on Android;
- the content widget is manually sized to exactly the live viewport width;
- automatic QScrollArea child-size negotiation is disabled;
- quick-date actions reflow to one column on narrow phones and two columns on wider screens;
- the calendar keeps seven equal columns within the viewport;
- vertical scrolling remains enabled.
