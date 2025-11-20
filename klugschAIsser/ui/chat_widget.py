import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QLabel, QScrollArea)
from PySide6.QtCore import Qt, QTimer, QThread
# Importiere Backend-Logik
from klugschAIsser.core.ollama_client import OllamaClient
from klugschAIsser.core.worker import OllamaWorker


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ollama_client = OllamaClient()  # Verbindung zu Ollama
        self.conversation_history = []
        self.worker_thread = None

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Scroll-Bereich für Nachrichten
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.chat_layout = QVBoxLayout(self.scroll_content)
        self.chat_layout.addStretch()  # Drückt Nachrichten nach unten
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

    def send_message(self):
        text = self.input_field.text().strip()
        if not text: return

        # User Nachricht anzeigen
        self._add_bubble(text, is_user=True)
        self.conversation_history.append({'role': 'user', 'content': text})
        self.input_field.clear()
        self.input_field.setEnabled(False)  # Eingabe sperren während Generierung

        # Threading für LLM (verhindert UI-Freeze)
        self.thread = QThread()
        self.worker = OllamaWorker(self.ollama_client, self.conversation_history)
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
            self.current_llm_bubble = self._add_bubble("", is_user=False)

        self.full_response += chunk
        self.current_llm_bubble.setText(self.full_response)
        self._scroll_to_bottom()

    def _finalize_stream(self):
        """Wenn die Antwort fertig ist"""
        self.conversation_history.append({'role': 'assistant', 'content': self.full_response})
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self.thread.quit()

    def _add_bubble(self, text, is_user):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # CSS Klasse für Styling zuweisen
        label.setProperty("class", "user-bubble" if is_user else "llm-bubble")

        # Maximale Breite der Bubble
        label.setMaximumWidth(int(self.width() * 0.7))

        h_layout = QHBoxLayout()
        if is_user:
            h_layout.addStretch()
            h_layout.addWidget(label)
        else:
            h_layout.addWidget(label)
            h_layout.addStretch()

        self.chat_layout.insertLayout(self.chat_layout.count() - 1, h_layout)
        self._scroll_to_bottom()
        return label

    def _scroll_to_bottom(self):
        # Scrollt automatisch nach unten
        sb = self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())