from pathlib import Path

# Central repository for all design parameters (colors, fonts, etc.)
# This makes it easy to change the application's appearance globally.
THEME = {
    "COLORS": {
        "PRIMARY_BLUE": "#3b82f6",
        "USER_BUBBLE": "#2563eb",
        "LLM_BUBBLE": "#4b5563",
        "BACKGROUND_DARK": "#111827",
        "BACKGROUND_MEDIUM": "#1f2937",
        "BACKGROUND_LIGHT": "#374151",
        "TEXT_LIGHT": "#f9fafb",
        "TEXT_DARK": "#e5e7eb",
        "BORDER": "#4b5563",
    },
    "FONTS": {
        "FAMILY": "Segoe UI",
        "SIZE_NORMAL": "14px",
        "SIZE_LARGE": "16px",
    },
    "SPACING": {
        "SMALL": "5px",
        "MEDIUM": "10px",
        "LARGE": "15px",
    },
    "RADIUS": {
        "SMALL": "5px",
        "MEDIUM": "10px",
        "LARGE": "15px",  # For the pill-shaped bubbles
    }
}


def load_stylesheet():
    """
    Loads the QSS template file, replaces placeholders with theme values,
    and returns the complete stylesheet string.
    """
    qss_path = Path(__file__).parent / "style.qss"
    try:
        with open(qss_path, "r") as f:
            stylesheet = f.read()

        # Replace all placeholders in the QSS file
        for category, values in THEME.items():
            for key, value in values.items():
                placeholder = f"{{{{{category}.{key}}}}}"
                stylesheet = stylesheet.replace(placeholder, value)

        return stylesheet
    except FileNotFoundError:
        print(f"Error: Stylesheet file not found at {qss_path}")
        return ""  # Return empty string if file is not found
