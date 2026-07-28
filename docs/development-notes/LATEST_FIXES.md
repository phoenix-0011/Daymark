# Latest Android UI fixes

- Replaced the custom button-based dropdown popup with a QListWidget-based touch popup.
- Day, month, category, repeat, and reminder selectors now use per-pixel kinetic scrolling.
- Repeat and reminder display all items without an internal scrollbar when the screen has room.
- The current selection is centered when opening a long list.
- Notes in New/Edit Task are three lines tall and scroll internally for longer text.
- Rebuilt compact Week layout sizing so an entirely empty week remains aligned.
- Removed stretch factors from empty day cards; only the bottom spacer expands.
- Week refreshes preserve scroll position within the same week and reset at a new week.
- Existing successful Android export configuration is preserved:
  - plugins = platforms_qtforandroid
  - local_libs is empty
  - SDK and NDK are passed explicitly.
