import ollama

class OllamaClient:
    def __init__(self, model='gemma3:1b'): # Modell anpassen falls nötig
        self.model = model
        self.client = ollama.Client()

    def chat(self, messages):
        try:
            stream = self.client.chat(model=self.model, messages=messages, stream=True)
            for chunk in stream:
                yield chunk['message']['content']
        except Exception as e:
            yield f"Error: {str(e)}"