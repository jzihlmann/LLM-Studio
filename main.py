import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QHBoxLayout, QListWidget, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from ollama import chat, ChatResponse


class ChatWindow(QWidget):
    """
    Diese Klasse erstellt das Hauptfenster für die Chat-Anwendung,
    basierend auf dem UI/UX Designkonzept "Professional Minimalism".
    """

    def __init__(self):
        super().__init__()
        # Speichert die gesamte Konversation im Format, das die Ollama-API erwartet.
        self.messages = []
        self.initUI()

    def initUI(self):
        """
        Initialisiert die Benutzeroberfläche, erstellt die Widgets und legt das Layout fest.
        """
        self.setWindowTitle('klugschAIsser')
        self.resize(1024, 768)  # Anpassbare Startgröße

        # Hauptlayout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Kein Rand um das Hauptfenster

        # Linke Seitenleiste für Chat-Verlauf
        self.sidebar = QListWidget()
        self.sidebar.addItem("Chat von Gestern")
        self.sidebar.addItem("Wichtige Notizen")
        self.sidebar.addItem("Neuer Chat")
        self.sidebar.setCurrentRow(2)  # Wählt "Neuer Chat" aus

        # Haupt-Inhaltsbereich (Chat + Eingabe)
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(10, 10, 10, 10)

        # Anzeigefenster für den Chatverlauf
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        # Initial greeting message styled as an assistant bubble
        initial_message = "Hallo! Womit kann ich heute helfen?"
        initial_html = f"""
        <div align='left' style='margin-left: 10px; margin-bottom: 12px;'>
            <div style='font-size: 10px; color: #b2bec3; margin-left: 10px; margin-bottom: 3px;'>Assistent</div>
            <div style='background-color: #636e72; color: white; display: inline-block; padding: 12px; border-radius: 18px; border-bottom-left-radius: 0; max-width: 80%; text-align: left;'>
                {initial_message}
            </div>
        </div>
        """
        self.chat_display.setHtml(initial_html)
        chat_layout.addWidget(self.chat_display)

        # Eingabefeld für den Benutzer
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Schreiben Sie Ihre Nachricht hier...")
        self.input_field.returnPressed.connect(self.send_message)
        chat_layout.addWidget(self.input_field)

        # Senden-Button
        self.send_button = QPushButton("Senden")
        self.send_button.clicked.connect(self.send_message)
        chat_layout.addWidget(self.send_button)

        # QSplitter für anpassbare Größenverhältnisse
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(chat_container)
        splitter.setSizes([250, 750])  # Startgrößen für Seitenleiste und Hauptbereich

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        self.apply_styles()  # Wendet das neue Stylesheet an

    def apply_styles(self):
        """
        Definiert und wendet ein QSS-Stylesheet an, um das Aussehen der App zu modernisieren.
        Inspiriert von PyCharm Dark Mode und "Focused Glassmorphism".
        """
        stylesheet = """
            QWidget {
                background-color: #2b2b2b; /* PyCharm Dark Background */
                color: #dfe6e9;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QListWidget { /* Seitenleiste */
                background-color: rgba(50, 50, 50, 0.8); /* "Milchglas"-Effekt */
                border: none;
                font-size: 13px;
                padding-top: 10px;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #0984e3; /* Akzentfarbe für Auswahl */
                color: white;
            }
            QTextEdit {
                background-color: #3c3f41; /* Etwas hellerer Hintergrund für den Chat */
                border: 1px solid #323232;
                border-radius: 8px;
            }
            QLineEdit {
                background-color: #45494a;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 1px solid #0984e3; /* Akzentfarbe bei Fokus */
            }
            QPushButton {
                background-color: #0984e3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74b9ff;
            }
            QPushButton:pressed {
                background-color: #005cb8;
            }
            QSplitter::handle {
                background-color: #3c3f41;
            }
            QSplitter::handle:horizontal {
                width: 1px;
            }
        """
        self.setStyleSheet(stylesheet)

    def send_message(self):
        """
        Wird aufgerufen, wenn der Senden-Button geklickt oder Enter gedrückt wird.
        Holt den Text, zeigt ihn an, sendet ihn an Ollama und zeigt die Antwort an.
        """
        user_input = self.input_field.text().strip()

        if user_input:
            # User chat bubble (right aligned)
            user_message_html = f"""
            <div align='right' style='margin-right: 10px; margin-bottom: 12px;'>
                <div style='font-size: 10px; color: #b2bec3; margin-right: 10px; margin-bottom: 3px;'>Du</div>
                <div style='background-color: #0984e3; color: white; display: inline-block; padding: 12px; border-radius: 18px; border-bottom-right-radius: 0; max-width: 80%; text-align: left;'>
                    {user_input}
                </div>
            </div>
            """
            self.chat_display.moveCursor(QTextCursor.End)
            self.chat_display.insertHtml(user_message_html)

            self.messages.append({'role': 'user', 'content': user_input})
            self.input_field.clear()

            # Deaktivieren der Eingabe während der Bot antwortet
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
            QApplication.processEvents()  # UI aktualisieren

            try:
                # Verwende 'gemma'. Ändern Sie dies, wenn Sie ein anderes Ollama-Modell verwenden.
                response: ChatResponse = chat(model='gemma3:1b', messages=self.messages)
                assistant_response = response['message']['content']
                self.messages.append({'role': 'assistant', 'content': assistant_response})

                # Assistant chat bubble (left aligned)
                assistant_message_html = f"""
                <div align='left' style='margin-left: 10px; margin-bottom: 12px;'>
                    <div style='font-size: 10px; color: #b2bec3; margin-left: 10px; margin-bottom: 3px;'>Assistent</div>
                    <div style='background-color: #636e72; color: white; display: inline-block; padding: 12px; border-radius: 18px; border-bottom-left-radius: 0; max-width: 80%; text-align: left;'>
                        {assistant_response}
                    </div>
                </div>
                """
                self.chat_display.moveCursor(QTextCursor.End)
                self.chat_display.insertHtml(assistant_message_html)

            except Exception as e:
                error_message = f"<div style='color: #ff7675; padding: 10px;'>Fehler: {e}</div>"
                self.chat_display.moveCursor(QTextCursor.End)
                self.chat_display.insertHtml(error_message)
            finally:
                self.input_field.setEnabled(True)
                self.send_button.setEnabled(True)
                self.input_field.setFocus()

            self.chat_display.ensureCursorVisible()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    window = ChatWindow()
    window.show()

    sys.exit(app.exec())

