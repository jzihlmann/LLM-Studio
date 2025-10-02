import sys
from PySide6.QtWidgets import QApplication
from klugschAIsser.ui.main_window import MainWindow

# This is the main entry point of the application.
if __name__ == "__main__":
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Run the application's event loop
    sys.exit(app.exec())
