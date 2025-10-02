from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QPushButton, QListWidget)
from PySide6.QtCore import Qt, QSize

from klugschAIsser.ui.theme import load_stylesheet
from klugschAIsser.ui.chat_widget import ChatWidget


class MainWindow(QMainWindow):
    """
    The main window of the application, organizing the different UI components.
    It follows the three-part "Bento" layout described in the concept.
    """

    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.setWindowTitle("KlugschAIsser MVP")
        self.setGeometry(100, 100, 1000, 600)  # x, y, width, height

        # --- Apply Stylesheet ---
        # Load the theme-based stylesheet for a consistent look and feel.
        stylesheet = load_stylesheet()
        self.setStyleSheet(stylesheet)

        # --- Main Layout ---
        # The central widget will hold all other components.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout for the whole window
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- 1. Top Navigation ---
        top_nav_widget = self._create_top_nav()
        main_layout.addWidget(top_nav_widget)

        # --- 2. Main Content Area (Sidebar + Chat) ---
        main_content_widget = self._create_main_content()
        main_layout.addWidget(main_content_widget, 1)  # The '1' makes this area expand

    def _create_top_nav(self):
        """Creates the top navigation bar widget."""
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        chat_button = QPushButton("Chat")
        chat_button.setObjectName("top_nav_button")  # For specific styling
        chat_button.setFlat(True)
        nav_layout.addWidget(chat_button)

        return nav_widget

    def _create_main_content(self):
        """Creates the main content widget containing the sidebar and chat area."""
        content_widget = QWidget()
        # Use object name for specific styling of the main background
        content_widget.setObjectName("main_content_widget")

        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # --- Left Sidebar ---
        # As per the MVP, this is just a placeholder.
        chat_history_list = QListWidget()
        chat_history_list.setMaximumWidth(250)
        # TODO: This will later be populated with past chat sessions.

        # --- Chat Widget (Main Area) ---
        chat_widget = ChatWidget()

        # Add sidebar and chat widget to the layout
        content_layout.addWidget(chat_history_list)
        content_layout.addWidget(chat_widget, 1)  # The '1' makes the chat widget expand

        return content_widget
