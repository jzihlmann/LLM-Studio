import ollama


class OllamaClient:
    def __init__(self, model='gemma3:1b'):
        self.model = model
        # WICHTIG: AsyncClient statt normaler Client
        # Das erlaubt uns, auf Antworten zu warten, ohne das ganze Programm zu blockieren.
        self.client = ollama.AsyncClient()

    async def chat(self, messages):
        """
        Asynchroner Generator.
        'async def' markiert die Funktion als coroutine (pausierbar).
        """
        try:
            # 'await' gibt die Kontrolle kurz an das System zurück, bis Ollama antwortet
            stream = await self.client.chat(
                model=self.model,
                messages=messages,
                stream=True
            )

            # 'async for' iteriert durch die Antwortschnipsel, sobald sie eintreffen
            async for chunk in stream:
                content = chunk.get('message', {}).get('content', '')
                if content:
                    yield content

        except Exception as e:
            # Fehler auch als Text zurückgeben, damit er im Chat erscheint
            yield f"Error: {str(e)}"