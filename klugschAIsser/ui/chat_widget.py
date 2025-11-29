from nicegui import ui
from klugschAIsser.core.ollama_client import OllamaClient
from klugschAIsser.core.types import ChatMessage, ChatSession


class ChatWidget:
    def __init__(self):
        self.client = OllamaClient()
        self.active_session = None

        # UI-Referenzen
        self.chat_container = None
        self.input_field = None
        self.footer = None

    def build(self):
        """Erstellt die UI-Elemente für den Chat."""

        # 1. Nachrichten-Bereich
        with ui.column().classes('w-full max-w-4xl mx-auto p-4 gap-8 pb-32') as self.chat_container:
            if not self.active_session:
                ui.label('Bitte wähle oder erstelle einen Chat.').classes('text-gray-500 italic')
            else:
                self._render_messages()

        # 2. Eingabe-Bereich (Fixed Bottom)
        with ui.footer().classes('bg-slate-900/90 no-shadow p-4 z-50'):

            with ui.row().classes(
                    'w-full max-w-4xl mx-auto bg-slate-800 rounded-xl px-4 py-2 items-end border border-gray-700 shadow-2xl') as self.footer:
                # ÄNDERUNG: input-style hinzugefügt
                # max-height: 50vh -> Maximal 50% der Fensterhöhe
                # overflow-y: auto -> Scrollbalken erscheint, wenn Text länger ist
                self.input_field = ui.textarea(placeholder='Frag KlugschAIsser...') \
                    .classes('w-full text-gray-100 bg-transparent') \
                    .props('dark borderless autogrow rows=1 input-style="max-height: 50vh; overflow-y: auto"') \
                    .on('keydown.enter.prevent', self.handle_enter, args=['shiftKey'])

                with self.input_field.add_slot('append'):
                    ui.button(icon='send', on_click=self.send_message) \
                        .props('flat round dense text-color=blue') \
                        .classes('mb-1')

    async def handle_enter(self, e):
        """Entscheidet anhand der Shift-Taste, was passiert."""
        if e.args['shiftKey']:
            # Shift+Enter: Zeilenumbruch manuell einfügen
            self.input_field.value = (self.input_field.value or "") + "\n"
        else:
            # Nur Enter: Senden
            await self.send_message()

    def set_session(self, session: ChatSession):
        self.active_session = session
        self.chat_container.clear()
        with self.chat_container:
            self._render_messages()

    def _render_messages(self):
        if not self.active_session: return
        for msg in self.active_session.messages:
            self._create_message_element(msg.content, is_user=(msg.role == 'user'))

    def _create_message_element(self, text, is_user):
        if is_user:
            # USER: Rechtsbündig
            with ui.row().classes('w-full justify-end items-end gap-2'):
                with ui.card().classes('bg-blue-600 text-white p-3 rounded-2xl rounded-tr-none max-w-[50%]'):
                    ui.markdown(text).classes('text-base whitespace-pre-wrap')
                ui.avatar(icon='person', color='blue-800', text_color='white').classes('mb-1')
        else:
            # BOT: Linksbündig, Flat Design
            with ui.row().classes('w-full items-start gap-4 animate-fade'):
                ui.avatar(icon='smart_toy', color='blue-grey-9', text_color='white').classes('mt-1')
                with ui.column().classes('flex-grow min-w-0 spacing-y-1'):
                    ui.label('KlugschAIsser').classes('text-blue-400 text-xs font-bold mb-1')
                    content = ui.markdown(text).classes('w-full text-gray-200 leading-relaxed')
                    return content

    async def send_message(self):
        if not self.active_session: return

        text = self.input_field.value
        if not text or not text.strip(): return

        self.input_field.value = ''

        # User Nachricht anzeigen
        with self.chat_container:
            self._create_message_element(text, is_user=True)

        self.active_session.messages.append(ChatMessage(role='user', content=text))

        # Platzhalter für Bot
        with self.chat_container:
            spinner_row = ui.row().classes('items-center gap-2')
            with spinner_row:
                ui.avatar(icon='smart_toy', color='blue-grey-9', text_color='white')
                ui.spinner(size='1.5em', color='blue-400')

            response_markdown = self._create_message_element("", is_user=False)

        # LLM Streaming
        full_response = ""
        history_dicts = [m.to_ollama_dict() for m in self.active_session.messages]

        try:
            first_chunk = True
            async for chunk in self.client.chat(history_dicts):
                if first_chunk:
                    spinner_row.delete()
                    first_chunk = False

                full_response += chunk
                if response_markdown:
                    response_markdown.content = full_response

                ui.run_javascript("window.scrollTo(0, document.body.scrollHeight);")

        except Exception as e:
            ui.notify(f"Fehler: {e}", type='negative')
            if 'spinner_row' in locals(): spinner_row.delete()

        bot_msg = ChatMessage(role='assistant', content=full_response)
        self.active_session.messages.append(bot_msg)
        self.active_session.update_title_from_content()