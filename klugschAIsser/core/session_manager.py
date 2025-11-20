from typing import List, Optional
from uuid import UUID
from klugschAIsser.core.types import ChatSession, BotProfile


class SessionManager:
    def __init__(self):
        self.sessions: List[ChatSession] = []
        self.active_session: Optional[ChatSession] = None

        # Standard-Bot (UUID ist hier dynamisch, später fixieren wir das evtl.)
        self.default_bot = BotProfile(name="Gemma", ollama_model="gemma3:1b")

    def create_new_session(self) -> ChatSession:
        """Erstellt eine neue Session und setzt sie als aktiv."""
        session = ChatSession()
        self.sessions.insert(0, session)  # Neue Session oben in die Liste
        self.active_session = session
        return session

    def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        for s in self.sessions:
            if s.id == session_id:
                return s
        return None