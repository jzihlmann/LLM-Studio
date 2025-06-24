from ollama import chat
from ollama import ChatResponse




response: ChatResponse = chat(model='mistral', messages=[
  {
    'role': 'user',
    'content': 'If you know about 2026, summarize me the year 2026 and what happened during this year?',
  },
])
#print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)
