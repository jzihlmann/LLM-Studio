import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor # Import für den Text-Cursor hinzugefügt
from ollama import chat, ChatResponse


class ChatWindow(QWidget):
    """
    Diese Klasse erstellt das Hauptfenster für die Chat-Anwendung.
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
        self.setWindowTitle('KlugschAIsser MVP')
        self.setGeometry(100, 100, 600, 800)

        # Layout-Container
        layout = QVBoxLayout()

        # Anzeigefenster für den Chatverlauf
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        # Wir verwenden HTML, um die Sprechblasen zu formatieren.
        self.chat_display.setHtml("<div style='padding: 10px;'>Hallo Julian! Was möchtest du wissen?</div>")
        layout.addWidget(self.chat_display)

        # Eingabefeld für den Benutzer
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Schreibe deine Nachricht hier...")
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)

        # Senden-Button
        self.send_button = QPushButton("Senden")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)
        self.apply_styles() # Wendet das neue Stylesheet an

    def apply_styles(self):
        """
        Definiert und wendet ein QSS-Stylesheet an, um das Aussehen der App zu modernisieren.
        QSS ist analog zu CSS im Webdesign.
        """
        stylesheet = """
            QWidget {
                background-color: #2d3436; /* Dunkler Hintergrund */
                color: #dfe6e9; /* Heller Text */
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #454e54;
                border: 1px solid #636e72;
                border-radius: 8px;
            }
            QLineEdit {
                background-color: #636e72;
                border: 1px solid #b2bec3;
                border-radius: 8px;
                padding: 8px;
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
                background-color: #74b9ff; /* Heller bei Mouse-Over */
            }
            QPushButton:pressed {
                background-color: #005cb8; /* Dunkler bei Klick */
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
            # NEUE HTML-STRUKTUR: Verwendet eine unsichtbare Tabelle für ein robustes Layout.
            user_message_html = f"""
            <table width='100%'>
                <tr>
                    <td></td>
                    <td align='right' style='padding-right: 10px; margin-bottom: 15px;'>
                        <div style='font-size: 10px; color: #b2bec3; margin-right: 10px; margin-bottom: 3px;'>Du</div>
                        <div style='background-color: #0984e3; color: white; display: inline-block; padding: 10px; border-radius: 15px 15px 0 15px; max-width: 100%; text-align: left;'>
                            {user_input}
                        </div>
                    </td>
                </tr>
            </table>
            """
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertHtml(user_message_html)
            self.chat_display.setTextCursor(cursor)

            self.messages.append({'role': 'user', 'content': user_input})
            self.input_field.clear()

            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
            QApplication.processEvents()

            try:
                response: ChatResponse = chat(model='mistral', messages=self.messages)
                assistant_response = response['message']['content']
                self.messages.append({'role': 'assistant', 'content': assistant_response})

                # NEUE HTML-STRUKTUR: Auch hier wird die Tabelle für die Ausrichtung verwendet.
                assistant_message_html = f"""
                <table width='100%'>
                    <tr>
                        <td align='left' style='padding-left: 10px; margin-bottom: 15px;'>
                            <div style='font-size: 10px; color: #b2bec3; margin-left: 10px; margin-bottom: 3px;'>Assistent</div>
                            <div style='background-color: #636e72; color: white; display: inline-block; padding: 10px; border-radius: 15px 15px 15px 0; max-width: 100%; text-align: left;'>
                                {assistant_response}
                            </div>
                        </td>
                        <td></td>
                    </tr>
                </table>
                """
                cursor = self.chat_display.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertHtml(assistant_message_html)
                self.chat_display.setTextCursor(cursor)

            except Exception as e:
                error_message = f"<div style='color: #ff7675; padding: 10px;'>Fehler: {e}</div>"
                cursor = self.chat_display.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.insertHtml(error_message)
                self.chat_display.setTextCursor(cursor)
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
