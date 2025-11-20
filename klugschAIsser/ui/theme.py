from pathlib import Path

THEME = {
    "COLORS": {
        "BACKGROUND_DARK": "#111827",  # Hauptfenster Hintergrund
        "BACKGROUND_MEDIUM": "#1f2937",  # Fallback
        "BACKGROUND_LIGHT": "#374151",  # Eingabefelder

        # NEU: Liquid Glass Definitionen
        # Wir nutzen RGBA für Transparenz
        "GLASS_BG": "rgba(31, 41, 55, 0.6)",  # Dunkel, leicht transparent
        "GLASS_BORDER": "rgba(255, 255, 255, 0.08)",  # Subtiler heller Rand für 3D

        "PRIMARY": "#3b82f6",
        "TEXT": "#f9fafb",
        "USER_BUBBLE": "#2563eb",
        "LLM_BUBBLE": "#4b5563"
    }
}


def load_stylesheet():
    path = Path(__file__).parent / "style.qss"
    # Fehlerbehandlung, falls Datei nicht existiert
    if not path.exists():
        return ""

    with open(path, "r") as f:
        style = f.read()

    for key, val in THEME["COLORS"].items():
        style = style.replace(f"{{{{COLORS.{key}}}}}", val)
    return style