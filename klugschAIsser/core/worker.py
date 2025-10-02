from PySide6.QtCore import QObject, Signal


class OllamaWorker(QObject):
    """
    A worker object that runs in a separate thread to handle Ollama API calls.
    This version is updated to handle streaming responses, emitting signals for
    each chunk of data received and a final signal when the stream is complete.
    """
    # Signal to emit each chunk of the response
    chunk_received = Signal(str)
    # Signal to emit when the entire stream is finished
    finished = Signal()

    def __init__(self, ollama_client, messages):
        super().__init__()
        self.ollama_client = ollama_client
        self.messages = messages

    def run(self):
        """
        Executes the streaming chat call and emits the response chunks.
        """
        # The ollama_client.chat method is now a generator
        response_generator = self.ollama_client.chat(self.messages)
        for chunk in response_generator:
            self.chunk_received.emit(chunk)

        # Signal that the entire process is complete
        self.finished.emit()

