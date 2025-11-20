from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QPushButton, QListWidget)
from PySide6.QtCore import Qt

from klugschAIsser.ui.theme import load_stylesheet
from klugschAIsser.ui.chat_widget import ChatWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Fenster ---
        self.setWindowTitle("KlugschAIsser MVP")
        self.setGeometry(100, 100, 1200, 800)

        # Stylesheet laden
        self.setStyleSheet(load_stylesheet())

        # --- Zentrales Widget ---
        # Dies ist der dunkle Hintergrund, auf dem die "Glas-Platten" liegen
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # --- Layout-Struktur für das "T" ---
        # Wir nutzen ein vertikales Layout für (Oben) und (Unten)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)  # Rand zum Fensterrand
        main_layout.setSpacing(15)  # Abstand zwischen Nav und Content (Der waagrechte Balken des T)

        # --- 1. Oben: Navigation Container ---
        self.nav_container = self._create_nav_container()
        main_layout.addWidget(self.nav_container)

        # --- 2. Unten: Split Bereich (Sidebar | Chat) ---
        # Ein horizontales Layout für die beiden unteren Boxen
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)  # Abstand zwischen Sidebar und Chat (Der senkrechte Balken des T)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # A. Linke Sidebar Box
        self.sidebar_container = self._create_sidebar_container()
        bottom_layout.addWidget(self.sidebar_container)

        # B. Rechte Chat Box
        self.chat_container = self._create_chat_container()
        bottom_layout.addWidget(self.chat_container, 1)  # 1 = Chat nimmt Restplatz

        # Bottom Layout in Main Layout einfügen
        main_layout.addLayout(bottom_layout, 1)  # 1 = Unterer Bereich dehnt sich vertikal aus

    def _create_nav_container(self):
        """Erstellt die obere Navigations-Leiste als Bento-Box."""
        container = QWidget()
        container.setObjectName("container_nav")  # ID für CSS Styling

        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)

        # Zentrierter Button durch "Stretch" links und rechts
        chat_btn = QPushButton("Chat")
        chat_btn.setObjectName("top_nav_button")
        chat_btn.setFlat(True)
        chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addStretch()
        layout.addWidget(chat_btn)
        layout.addStretch()

        return container

    def _create_sidebar_container(self):
        """Erstellt die Sidebar als Bento-Box."""
        container = QWidget()
        container.setObjectName("container_sidebar")  # ID für CSS Styling
        container.setFixedWidth(260)  # Feste Breite für die Sidebar-Box

        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)

        # Inhalt: Liste (Aktuell leerer Platzhalter)
        list_widget = QListWidget()
        layout.addWidget(list_widget)

        return container

    def _create_chat_container(self):
        """Erstellt den Chat-Bereich als Bento-Box."""
        container = QWidget()
        container.setObjectName("container_chat")  # ID für CSS Styling

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)  # Kein Innenabstand, ChatWidget regelt das

        # Chat Logik einbinden
        chat_widget = ChatWidget()

        # WICHTIG: Damit der Hintergrund des ChatWidgets transparent ist
        # und der Container-Style (#container_chat) sichtbar bleibt:
        chat_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout.addWidget(chat_widget)

        return container