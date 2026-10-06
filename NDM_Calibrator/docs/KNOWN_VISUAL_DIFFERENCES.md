# Known Visual Differences

- Recharts uses browser text and line rasterization; PyQtGraph uses Qt font and
  OpenGL/painter paths. Axis baselines, ticks and anti-aliasing differ slightly.
- Qt content is somewhat denser at the 1440x900 capture size.
- Identification logarithmic Y-axis labels use PyQtGraph formatting rather
  than the browser chart's decimal formatting.
- Data field mapping uses a `QComboBox` delegate; Qt renders the closed editor
  more compactly than the browser select control.
- Lucide-derived Qt icons are slightly smaller/lighter after rasterization.
- Qt logs a missing Conda font-directory warning. Microsoft YaHei font files
  are loaded explicitly, and Chinese glyphs render correctly in captures.
- Offscreen pytest emits a non-failing QObject timer-thread warning after the
  migration suite; visible application behavior and screenshots are unaffected.

## Implementation-Scope Differences

- Sidebar collapse is an immediate `setFixedWidth()` change in Qt. The Web
  prototype animates the same 220/68 px transition over 160 ms.
- The collapsed sidebar state is kept in memory for the current application
  session. The migration does not persist it with `QSettings`.
- The migration is intentionally fixed to the frozen Light theme. The Topbar
  theme action reports that scope; there is no Light/Dark palette or chart
  theme switch in this Mock version.
- Identification is a deterministic `QTimer`-driven Mock on the UI event loop.
  It does not use a worker `QThread` or connect to a real optimization/backend;
  the short demo states are the behavior covered by the migration tests.
