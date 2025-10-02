import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QLabel, QScrollArea)
from PySide6.QtCore import Qt, QTimer, QThread
from klugschAIsser.core.ollama_client import OllamaClient
from klugschAIsser.core.worker import OllamaWorker


class ChatWidget(QWidget):
    """
    A widget that provides a chat interface.
    This version is updated to handle and display streaming LLM responses.
    """

    def __init__(self):
        super().__init__()

        # --- Member Variables ---
        self.ollama_client = OllamaClient()
        self.conversation_history = []
        self.worker_thread = None
        self.worker = None
        self.typing_indicator = None
        self.current_llm_bubble = None  # Holds the bubble being updated by the stream
        self.full_llm_response = ""  # Accumulates the full response for history

        # --- Main Layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Message Display Area ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_content_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.scroll_content_widget)
        self.chat_layout.addStretch()
        self.chat_layout.setSpacing(10)
        self.scroll_area.setWidget(self.scroll_content_widget)

        # --- Input Area ---
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        # --- Assemble Layout ---
        layout.addWidget(self.scroll_area)
        layout.addLayout(input_layout)

    def send_message(self):
        """
        Handles sending a user message and starting the streaming worker thread.
        """
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        self._add_message_to_display(user_message, is_user=True)
        self.conversation_history.append({'role': 'user', 'content': user_message})
        self.input_field.clear()

        self._show_typing_indicator()

        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)

        self.full_llm_response = ""  # Reset for the new message

        self.worker_thread = QThread()
        self.worker = OllamaWorker(self.ollama_client, self.conversation_history)
        self.worker.moveToThread(self.worker_thread)

        # Connect new streaming signals
        self.worker.chunk_received.connect(self._handle_llm_chunk)
        self.worker.finished.connect(self._handle_llm_finished)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def _handle_llm_chunk(self, chunk):
        """
        Receives a chunk of text from the stream and updates the display.
        """
        # On the first chunk, remove the indicator and create the bubble
        if self.current_llm_bubble is None:
            self._remove_typing_indicator()
            self.current_llm_bubble = self._create_bubble("", is_user=False)
            h_layout = QHBoxLayout()
            h_layout.addWidget(self.current_llm_bubble)
            h_layout.addStretch()
            self.chat_layout.insertLayout(self.chat_layout.count() - 1, h_layout)

        # Append new text and re-format
        self.full_llm_response += chunk
        formatted_text = self._format_text_to_html(self.full_llm_response)
        self.current_llm_bubble.setText(formatted_text)
        self._scroll_to_bottom()

    def _handle_llm_finished(self):
        """
        Called when the stream is complete.
        """
        # Add the complete response to the conversation history
        if self.full_llm_response:
            self.conversation_history.append({'role': 'assistant', 'content': self.full_llm_response})

        # Reset state and re-enable inputs
        self.current_llm_bubble = None
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
        self._scroll_to_bottom()

    def _add_message_to_display(self, text, is_user):
        """ Creates and adds a complete chat bubble widget to the chat layout. """
        bubble = self._create_bubble(text, is_user)
        h_layout = QHBoxLayout()

        if is_user:
            h_layout.addStretch()
            h_layout.addWidget(bubble)
        else:
            h_layout.addWidget(bubble)
            h_layout.addStretch()

        self.chat_layout.insertLayout(self.chat_layout.count() - 1, h_layout)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _format_text_to_html(self, text):
        """
        A simple converter from markdown-like text to a subset of HTML.
        """
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color: #60a5fa;">\1</a>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

        lines = text.split('\n')
        html_output = []
        in_ul = False

        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('* '):
                if not in_ul:
                    html_output.append('<ul style="margin: 0; padding-left: 20px;">')
                    in_ul = True
                html_output.append(f'<li>{stripped_line[2:]}</li>')
            else:
                if in_ul:
                    html_output.append('</ul>')
                    in_ul = False
                if stripped_line:
                    html_output.append(f'<p style="margin-top: 8px; margin-bottom: 8px;">{line}</p>')
        if in_ul:
            html_output.append('</ul>')

        return ''.join(html_output)

    def _create_bubble(self, text, is_user):
        """
        Creates a styled QLabel that can render rich text (HTML).
        """
        label = QLabel()
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextBrowserInteraction)
        label.setOpenExternalLinks(True)
        label.setTextFormat(Qt.RichText)

        if is_user:
            label.setText(text.replace('<', '&lt;'))
        else:
            formatted_text = self._format_text_to_html(text)
            label.setText(formatted_text)

        bubble_class = "user-bubble" if is_user else "llm-bubble"
        label.setProperty("class", bubble_class)

        label.setMaximumWidth(self.width() * 0.7)
        return label

    def _show_typing_indicator(self):
        """ Displays a temporary 'typing...' bubble. """
        self.typing_indicator = self._create_bubble("...", is_user=False)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.typing_indicator)
        h_layout.addStretch()

        self.chat_layout.insertLayout(self.chat_layout.count() - 1, h_layout)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _remove_typing_indicator(self):
        """ Removes the 'typing...' bubble. """
        if self.typing_indicator:
            for i in range(self.chat_layout.count()):
                layout_item = self.chat_layout.itemAt(i)
                if layout_item and layout_item.layout():
                    widget_item = layout_item.layout().itemAt(0)
                    if widget_item and widget_item.widget() == self.typing_indicator:
                        while layout_item.layout().count():
                            item = layout_item.layout().takeAt(0)
                            if item.widget():
                                item.widget().deleteLater()
                        self.chat_layout.removeItem(layout_item)
                        break
            self.typing_indicator = None

    def _scroll_to_bottom(self):
        """ Scrolls the chat view to the very bottom. """
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

