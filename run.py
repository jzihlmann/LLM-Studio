from nicegui import ui

# Importe aus unserer Core-Logik
from klugschAIsser.core.session_manager import SessionManager
from klugschAIsser.ui.chat_widget import ChatWidget

# Konstanten
THEME_COLORS = {
    "BACKGROUND_DARK": "#111827",
    "TEXT": "#f9fafb"
}

# --- State Initialisierung ---
session_manager = SessionManager()
if not session_manager.sessions:
    session_manager.create_new_session()

chat_widget = ChatWidget()


def create_layout():
    """Baut das Hauptlayout der Anwendung."""

    # Header
    # z-50: Hält den Header immer über dem Chat-Inhalt beim Scrollen
    with ui.header().classes('bg-slate-900 border-b border-gray-800 p-4 z-50') as header:
        # Hamburger-Menü Button
        # WICHTIG: Wir nutzen on_click mit einer Funktion, die den Drawer toggle't.
        # Da 'drawer' erst gleich definiert wird, ist das in Python kein Problem (Lambda fängt Variable später).
        ui.button(icon='menu', on_click=lambda: drawer.toggle()) \
            .props('flat round dense text-color=white') \
            .classes('mr-2')

        ui.label('KlugschAIsser Web [Alpha]').classes('text-xl font-bold text-gray-100')
        ui.space()
        ui.switch('Dark', value=True, on_change=lambda e: ui.dark_mode(e.value))

    # Sidebar (Links)
    # ÄNDERUNG: 'breakpoint=600' statt 'behavior="desktop"'
    # Das ist der Sweetspot:
    # - Auf kleinen Desktop-Fenstern (800px) bleibt sie offen (kein Overlay).
    # - Auf Handys (<600px) wird sie responsive und verdeckt den Inhalt nicht permanent.
    with ui.left_drawer(value=True).props('breakpoint=600 bordered').classes(
            'bg-slate-900 border-r border-gray-800') as drawer:
        drawer.style(f"background-color: {THEME_COLORS['BACKGROUND_DARK']}")

        with ui.row().classes('items-center justify-between w-full px-2 mb-4'):
            ui.label('Chats').classes('text-gray-400 text-sm font-bold')
            ui.button(icon='add', on_click=lambda: create_new_chat()).props('flat round text-color=blue')

        session_list_container = ui.column().classes('w-full px-2 gap-2')

        def refresh_sidebar():
            session_list_container.clear()
            with session_list_container:
                for session in session_manager.sessions:
                    btn = ui.button(session.title, on_click=lambda s=session: load_chat(s))
                    btn.props('flat align=left no-caps').classes('w-full text-gray-300 truncate')
                    if session == session_manager.active_session:
                        btn.classes('bg-gray-800 border border-gray-700')

        refresh_sidebar()

    # Canvas (Rechts)
    # right_drawer behält Standard-Breakpoint (1024), da der Canvas auf kleinen Screens
    # wirklich stört und besser als Overlay kommen sollte.
    with ui.right_drawer(value=False).props('bordered overlay').classes(
            'bg-slate-900 border-l border-gray-800') as canvas:
        canvas.props('width=500')
        ui.label('Canvas').classes('text-xl font-bold p-4 text-blue-400')

    # Hauptbereich (Chat)
    chat_widget.build()

    if session_manager.active_session:
        chat_widget.set_session(session_manager.active_session)

    # --- Logik ---
    def load_chat(session):
        session_manager.active_session = session
        chat_widget.set_session(session)
        refresh_sidebar()

    def create_new_chat():
        new_session = session_manager.create_new_session()
        load_chat(new_session)


@ui.page('/')
def main_page():
    ui.query('body').style(f"background-color: {THEME_COLORS['BACKGROUND_DARK']}; color: {THEME_COLORS['TEXT']}")
    ui.dark_mode().enable()
    create_layout()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='KlugschAIsser',
        port=8080,
        dark=True,
        native=True,
        reload=False
    )