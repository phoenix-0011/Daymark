# Schedule horizontal-fit fix

The schedule picker now clamps its body to the QScrollArea viewport on show and resize. This prevents Qt/Android size hints from creating a body wider than the phone. All seven calendar columns and all controls fit horizontally, while vertical scrolling remains available.
