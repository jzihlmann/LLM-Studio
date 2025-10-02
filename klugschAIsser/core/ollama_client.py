import ollama

class OllamaClient:
    """
    A client to interact with the Ollama API.
    This class handles sending chat messages and receiving responses.
    This version is updated to support streaming responses.
    """
    def __init__(self, model='gemma3:1b'):
        """
        Initializes the Ollama client.
        Args:
            model (str): The name of the Ollama model to use.
                         Defaults to 'gemma3:1b' as a starting point.
        """
        self.model = model
        self.client = ollama.Client()

    def get_models(self):
        """
        Fetches the list of available local models from Ollama.
        """
        try:
            return [model['name'] for model in self.client.list()['models']]
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    def chat(self, messages):
        """
        Sends a list of messages to the Ollama chat endpoint and yields the response chunks.
        Args:
            messages (list): A list of message dictionaries, following the
                             Ollama API structure (e.g., [{'role': 'user', 'content': 'Hi'}]).
        Yields:
            str: The content chunks of the assistant's response.
        """
        try:
            # Use stream=True to get a generator of response chunks.
            stream = self.client.chat(model=self.model, messages=messages, stream=True)
            for chunk in stream:
                yield chunk['message']['content']
        except ollama.ResponseError as e:
            print(f"Ollama Response Error: {e.error}")
            yield f"Error: Could not connect to Ollama. Is the model '{self.model}' available?"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            yield "An unexpected error occurred. Is Ollama running?"

