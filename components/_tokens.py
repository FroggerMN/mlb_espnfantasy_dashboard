"""
components/_tokens.py

Single source of truth for the Notion-style design system.
All components import tokens from here to ensure visual consistency.
"""

# ============================================================
# Color Palette
# ============================================================

COLORS = {
    "bg_primary": "#FAFAF8",
    "bg_card": "#FFFFFF",
    "bg_filter": "#F5F5F3",
    "bg_sidebar": "#F7F7F5",
    "border": "#E5E5E0",
    "border_medium": "#D5D5D0",
    "text_primary": "#2F2F2F",
    "text_secondary": "#6F6F6F",
    "text_muted": "#9F9F9F",
    "accent": "#5B8A9A",
    "accent_hover": "#4A7585",
    "accent_light": "#EBF3F6",
    "accent_subtle": "rgba(91, 138, 154, 0.08)",
    "grid": "#EDEDEA",
    # Semantic colors
    "success_bg": "#ECFDF5",
    "success_text": "#065F46",
    "success_border": "#A7F3D0",
    "warning_bg": "#FFFBEB",
    "warning_text": "#92400E",
    "warning_border": "#FDE68A",
    "error_bg": "#FEF2F2",
    "error_text": "#991B1B",
    "error_border": "#FECACA",
    "info_bg": "#EFF6FF",
    "info_text": "#1E40AF",
    "info_border": "#BFDBFE",
}

# ============================================================
# Spacing Scale (px)
# ============================================================

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
}

# ============================================================
# Border Radius Scale (px)
# ============================================================

RADIUS = {
    "sm": 6,
    "md": 8,
    "lg": 12,
}

# ============================================================
# Typography
# ============================================================

FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

FONT_SIZES = {
    "h1": 30,
    "h2": 22,
    "h3": 18,
    "body": 15,
    "small": 13,
    "xs": 12,
}

# ============================================================
# Plotly Layout Defaults
# ============================================================

PLOTLY_LAYOUT_DEFAULTS = dict(
    font=dict(
        family=FONT_FAMILY,
        color=COLORS["text_primary"],
        size=13,
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=COLORS["bg_card"],
    xaxis=dict(
        gridcolor=COLORS["grid"],
        linecolor=COLORS["border"],
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor=COLORS["grid"],
        linecolor=COLORS["border"],
        zeroline=False,
    ),
    margin=dict(l=48, r=24, t=48, b=40),
    legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
)
