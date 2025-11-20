from PySide6.QtCore import QObject, Signal

class OllamaWorker(QObject):
    chunk_received = Signal(str)
    finished = Signal()

    def __init__(self, client, messages):
        super().__init__()
        self.client = client
        self.messages = messages

    def run(self):
        # Ruft die Streaming-Funktion auf
        for chunk in self.client.chat(self.messages):
            self.chunk_received.emit(chunk)
        self.finished.emit()