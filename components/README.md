# MLB Fantasy Dashboard — Component Library

A collection of reusable, Notion-style UI components for the Streamlit dashboard.

## Architecture

```
components/
├── __init__.py         # Public API — re-exports all components
├── _tokens.py          # Design tokens (colors, spacing, fonts, Plotly defaults)
├── cards.py            # notion_card (context manager), stat_card, kv_card
├── charts.py           # plotly_card — Plotly figure in a styled card
├── empty_states.py     # empty_state, no_data_card, missing_config_card
├── filters.py          # filter_dataframe — filterable dataframe widget
├── layout.py           # page_scaffold, spacer, divider, inject_notion_css
├── tables.py           # data_table — composite filter + card + dataframe + download
└── typography.py       # page_header, section_header, label_value, badge
```

## Quick Start

```python
from components import page_scaffold, section_header, notion_card, data_table, spacer

# Bootstrap the page (replaces 3 lines of boilerplate)
page_scaffold("My Page", "Description of this page.")

# Add a section with a data table
section_header("Rankings")
spacer(8)
data_table(df, key_prefix="rankings", enable_download=True)

# Wrap custom content in a card
with notion_card("Custom Section"):
    st.write("Any content here.")
```

## Component Reference

### Layout

| Component | Description |
|---|---|
| `page_scaffold(title, description, page_title, icon)` | One-call page bootstrap: `set_page_config` + CSS injection + page header |
| `spacer(px)` | Vertical whitespace (default 24px) |
| `divider()` | Styled horizontal rule |
| `inject_notion_css()` | Loads `assets/styles.css` into the page |

### Typography

| Component | Description |
|---|---|
| `page_header(title, description)` | H1 page title with optional subtitle |
| `section_header(title, description)` | H2 section header with optional subtitle |
| `label_value(label, value, sublabel)` | Small-caps label + large value display |
| `badge(text, variant)` | Status pill — variants: `success`, `warning`, `info`, `error` |

### Cards

| Component | Description |
|---|---|
| `notion_card(title, subtitle)` | Context manager card wrapper |
| `stat_card(label, value, sublabel)` | Metric-style card with label and value |
| `kv_card(title, items)` | Card with a key-value list (dict of label → value) |

### Tables

| Component | Description |
|---|---|
| `data_table(df, key_prefix, ...)` | All-in-one: filter bar + card-wrapped dataframe + optional download |

**Parameters:**
- `enable_filter` (bool, default `True`) — Show the filter bar
- `enable_download` (bool, default `False`) — Show CSV download button
- `download_filename` (str) — Filename for the download
- `download_label` (str) — Button label text
- `height` (int | None) — Fixed height for the dataframe widget

### Charts

| Component | Description |
|---|---|
| `plotly_card(fig, key, height)` | Wraps a Plotly figure in a card with design tokens applied |

### Empty States

| Component | Description |
|---|---|
| `empty_state(message, icon, show_icon)` | Generic empty-state card with optional icon |
| `no_data_card(message)` | Pre-configured "no roster data" message |
| `missing_config_card(message)` | Pre-configured "missing config" message |

### Filters

| Component | Description |
|---|---|
| `filter_dataframe(df, key_prefix, default_team)` | Filterable dataframe with auto-detected widget types |

### Design Tokens (`_tokens.py`)

| Token | Description |
|---|---|
| `COLORS` | Full color palette dict (21 tokens) |
| `SPACING` | Spacing scale: `xs=4, sm=8, md=12, lg=16, xl=24, xxl=32` |
| `RADIUS` | Border radius scale: `sm=6, md=8, lg=12` |
| `FONT_FAMILY` | Inter font stack string |
| `FONT_SIZES` | Font size scale: `h1=30, h2=22, h3=18, body=15, small=13, xs=12` |
| `PLOTLY_LAYOUT_DEFAULTS` | Dict of Plotly layout overrides matching the design system |

## Design System

### Colors
- **Background:** `#FAFAF8` (primary), `#FFFFFF` (card), `#F5F5F3` (filter)
- **Borders:** `#E5E5E0` (light), `#D5D5D0` (medium)
- **Text:** `#2F2F2F` (primary), `#6F6F6F` (secondary), `#9F9F9F` (muted)
- **Accent:** `#5B8A9A` (teal), `#4A7585` (hover), `#EBF3F6` (light)

### Spacing Scale
Use multiples from the scale: **4 · 8 · 12 · 16 · 24 · 32 px**

### Typography
- **H1:** 30px, weight 600
- **H2:** 22px, weight 600
- **H3:** 18px, weight 500
- **Body:** 15px, weight 400
- **Small:** 13px

### Component Shapes
- **Border radius:** 6–8px (cards, inputs), 12px (large containers)
- **Borders:** 1px solid `#E5E5E0`
- **Shadows:** `0 1px 2px rgba(0,0,0,0.04)` on hover

## Backward Compatibility

`utils/ui.py` is now a thin re-export layer that maps old function names
to their new `components.*` equivalents:

| Old Import | New Import |
|---|---|
| `from utils.ui import inject_notion_css` | `from components.layout import inject_notion_css` |
| `from utils.ui import notion_page_header` | `from components.typography import page_header` |
| `from utils.ui import notion_card_begin/end` | `from components.cards import notion_card` (context manager) |
| `from utils.ui import notion_badge` | `from components.typography import badge` |
| `from utils.ui import notion_spacer` | `from components.layout import spacer` |
| `from utils.ui import filter_dataframe` | `from components.filters import filter_dataframe` |
| `from utils.ui import NOTION_COLORS` | `from components._tokens import COLORS` |
| `from utils.ui import PLOTLY_LAYOUT_DEFAULTS` | `from components._tokens import PLOTLY_LAYOUT_DEFAULTS` |

**New code should import directly from `components`.**
