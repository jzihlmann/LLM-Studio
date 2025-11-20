from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QPushButton, QListWidget)
from PySide6.QtCore import Qt

from klugschAIsser.ui.theme import load_stylesheet
from klugschAIsser.ui.chat_widget import ChatWidget
from klugschAIsser.core.session_manager import SessionManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Daten-Manager initialisieren
        self.session_manager = SessionManager()
        # Initialer Chat
        self.session_manager.create_new_session()

        # --- Fenster ---
        self.setWindowTitle("KlugschAIsser MVP")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(load_stylesheet())

        # --- Zentrales Widget ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # --- Layout ---
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 1. Oben: Navigation
        self.nav_container = self._create_nav_container()
        main_layout.addWidget(self.nav_container)

        # 2. Unten: Sidebar & Chat
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # A. Sidebar (Reihenfolge wichtig: Erstellt self.session_list_widget)
        self.sidebar_container = self._create_sidebar_container()
        bottom_layout.addWidget(self.sidebar_container)

        # B. Chat
        self.chat_container = self._create_chat_container()
        bottom_layout.addWidget(self.chat_container, 1)

        main_layout.addLayout(bottom_layout, 1)

        # Nachdem alles erstellt ist, laden wir den ersten Chat
        self._refresh_sidebar_and_chat()

        # Signal verbinden: Wenn Titel im ChatWidget aktualisiert wird -> Sidebar neu laden
        # chat_container ist ein QWidget (Container), wir müssen auf das innere Widget zugreifen
        # Siehe _create_chat_container Implementierung unten
        self.chat_widget_instance.chat_title_updated.connect(self._update_sidebar_only)

    def _create_nav_container(self):
        container = QWidget()
        container.setObjectName("container_nav")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)

        chat_btn = QPushButton("Chat")
        chat_btn.setObjectName("top_nav_button")
        chat_btn.setFlat(True)
        chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addStretch()
        layout.addWidget(chat_btn)
        layout.addStretch()
        return container

    def _create_sidebar_container(self):
        container = QWidget()
        container.setObjectName("container_sidebar")
        container.setFixedWidth(260)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(10)

        # Neuer Chat Button
        new_chat_btn = QPushButton("+  Neuer Chat")
        new_chat_btn.setObjectName("btn_new_chat")
        new_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_chat_btn.clicked.connect(self.on_new_chat_clicked)
        layout.addWidget(new_chat_btn)

        # Liste für Sessions (WICHTIG: self. zuweisen, damit wir später darauf zugreifen können)
        self.session_list_widget = QListWidget()
        self.session_list_widget.itemClicked.connect(self.on_sidebar_item_clicked)
        layout.addWidget(self.session_list_widget)

        return container

    def _create_chat_container(self):
        container = QWidget()
        container.setObjectName("container_chat")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # ChatWidget Instanz speichern, damit wir Signale verbinden können
        self.chat_widget_instance = ChatWidget()
        self.chat_widget_instance.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout.addWidget(self.chat_widget_instance)
        return container

    # --- Logik ---

    def on_new_chat_clicked(self):
        self.session_manager.create_new_session()
        self._refresh_sidebar_and_chat()

    def on_sidebar_item_clicked(self, item):
        # Wir nutzen hier den Index der Liste, da er der Reihenfolge in sessions entspricht
        # (Achtung: funktioniert nur solange wir nicht sortieren/filtern)
        index = self.session_list_widget.row(item)
        session = self.session_manager.sessions[index]
        self.session_manager.active_session = session

        # Nur Chat laden, Sidebar muss nicht neu gebaut werden
        self.chat_widget_instance.load_session(
            session,
            self.session_manager.default_bot
        )

    def _refresh_sidebar_and_chat(self):
        """Lädt Sidebar neu und zeigt aktiven Chat an."""
        self._update_sidebar_only()

        if self.session_manager.active_session:
            # Chat Widget laden
            self.chat_widget_instance.load_session(
                self.session_manager.active_session,
                self.session_manager.default_bot
            )

            # Selektierung in der Liste korrigieren
            idx = self.session_manager.sessions.index(self.session_manager.active_session)
            self.session_list_widget.setCurrentRow(idx)

    def _update_sidebar_only(self):
        """Aktualisiert nur die Texte in der Liste."""
        self.session_list_widget.clear()
        for session in self.session_manager.sessions:
            self.session_list_widget.addItem(session.title)

        # Selektion wiederherstellen falls möglich
        if self.session_manager.active_session in self.session_manager.sessions:
            idx = self.session_manager.sessions.index(self.session_manager.active_session)
            self.session_list_widget.setCurrentRow(idx)