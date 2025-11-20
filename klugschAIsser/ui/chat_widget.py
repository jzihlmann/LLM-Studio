import re
import markdown
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QLabel, QScrollArea)
from PySide6.QtCore import Qt, QTimer, QThread, Signal

# Importiere Backend-Logik
from klugschAIsser.core.ollama_client import OllamaClient
from klugschAIsser.core.worker import OllamaWorker
from klugschAIsser.core.types import ChatSession, ChatMessage, BotProfile


class ChatWidget(QWidget):
    # Signal für Sidebar-Update (Titel)
    chat_title_updated = Signal()

    def __init__(self):
        super().__init__()
        self.ollama_client = OllamaClient()  # Verbindung zu Ollama

        # State Management für Sessions
        self.current_session = None
        self.current_bot_profile = None
        self.worker_thread = None

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Scroll-Bereich für Nachrichten
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("chat_scroll_content")  # Für CSS

        self.chat_layout = QVBoxLayout(self.scroll_content)
        self.chat_layout.addStretch()  # Drückt Nachrichten nach oben (Stretch ist unten)
        self.chat_layout.setSpacing(15)
        self.scroll_area.setWidget(self.scroll_content)

        # Eingabe-Bereich
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Nachricht eingeben...")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("Senden")
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)

        layout.addWidget(self.scroll_area)
        layout.addLayout(input_layout)

    def load_session(self, session: ChatSession, bot_profile: BotProfile):
        """Lädt eine existierende Session und stellt die Bubbles wieder her."""
        self.current_session = session
        self.current_bot_profile = bot_profile

        # 1. Alten Chat leeren (alles entfernen ausser dem Stretch am Ende)
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)  # Immer das oberste Element nehmen
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        # 2. Nachrichten wiederherstellen
        for msg in session.messages:
            self._add_bubble(msg.content, is_user=(msg.role == "user"))

        self.input_field.setFocus()

    def send_message(self):
        if not self.current_session:
            return

        text = self.input_field.text().strip()
        if not text: return

        # 1. UI Update (User Nachricht)
        self._add_bubble(text, is_user=True)
        self.input_field.clear()
        self.input_field.setEnabled(False)  # Eingabe sperren während Generierung

        # 2. Daten Update (In Session speichern)
        user_msg = ChatMessage(role="user", content=text)
        self.current_session.messages.append(user_msg)

        # Titel aktualisieren, falls es die erste Nachricht ist
        if self.current_session.update_title_from_content():
            self.chat_title_updated.emit()

        # 3. LLM Vorbereiten (Verlauf konvertieren)
        history_dicts = [m.to_ollama_dict() for m in self.current_session.messages]

        # Threading für LLM
        self.thread = QThread()
        self.worker = OllamaWorker(self.ollama_client, history_dicts)
        self.worker.moveToThread(self.thread)

        # Signale verbinden (Streaming Support)
        self.worker.chunk_received.connect(self._update_stream)
        self.worker.finished.connect(self._finalize_stream)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)

        self.current_llm_bubble = None
        self.full_response = ""
        self.thread.start()

    def _update_stream(self, chunk):
        """Wird für jedes Wort/Token aufgerufen"""
        if not self.current_llm_bubble:
            # Leere Bubble erstellen
            self.current_llm_bubble = self._add_bubble("", is_user=False)

        self.full_response += chunk

        # Live-Update: Markdown in HTML wandeln
        html_content = self._text_to_html(self.full_response)
        self.current_llm_bubble.setText(html_content)

        self._scroll_to_bottom()

    def _finalize_stream(self):
        """Wenn die Antwort fertig ist"""
        # Bot-Nachricht in Session speichern
        bot_id = str(self.current_bot_profile.id) if self.current_bot_profile else "unknown"

        # Sicherstellen, dass der letzte Stand sauber gerendert ist
        if self.current_llm_bubble:
            self.current_llm_bubble.setText(self._text_to_html(self.full_response))

        bot_msg = ChatMessage(
            role="assistant",
            content=self.full_response,  # Wir speichern das Original-Markdown, nicht das HTML!
            sender_id=bot_id
        )
        self.current_session.messages.append(bot_msg)

        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self.thread.quit()

    def _text_to_html(self, text):
        """Wandelt Markdown in HTML für das QLabel um."""
        # extensions:
        # 'fenced_code': Erlaubt Code-Blöcke mit ```
        # 'nl2br': Wandelt Newlines in <br> um, damit Zeilenumbrüche erhalten bleiben
        html = markdown.markdown(text, extensions=['fenced_code', 'nl2br'])
        return html

    def _add_bubble(self, text, is_user):
        # Konvertiere Text zu HTML für die Anzeige
        display_content = self._text_to_html(text)

        label = QLabel(display_content)
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)

        # WICHTIG: Damit HTML interpretiert wird
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setOpenExternalLinks(True)

        # CSS Klasse für Styling zuweisen
        label.setProperty("class", "user-bubble" if is_user else "llm-bubble")

        # Maximale Breite der Bubble (Fix gegen "Springen" und zu breite Texte)
        # Max 750px oder 85% der Fensterbreite
        max_width = min(750, int(self.width() * 0.85))
        label.setMaximumWidth(max_width)

        h_layout = QHBoxLayout()
        if is_user:
            h_layout.addStretch()
            h_layout.addWidget(label)
        else:
            h_layout.addWidget(label)
            h_layout.addStretch()

        # Einfügen VOR dem Stretch (Stretch ist das letzte Element)
        self.chat_layout.insertLayout(self.chat_layout.count() - 1, h_layout)
        self._scroll_to_bottom()
        return label

    def _scroll_to_bottom(self):
        # Scrollt automatisch nach unten
        sb = self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())