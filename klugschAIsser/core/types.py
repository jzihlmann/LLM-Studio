from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Dict, Any


@dataclass
class BotProfile:
    """Repräsentiert einen 'Assistenten'."""
    id: UUID = field(default_factory=uuid4)
    name: str = "Standard Assistent"
    ollama_model: str = "gemma3:1b"  # Technischer Modellname für Ollama
    system_prompt: str = ""


@dataclass
class ChatMessage:
    """Eine einzelne Nachricht."""
    id: UUID = field(default_factory=uuid4)
    role: str = "user"  # 'user' oder 'assistant'
    sender_id: str = ""  # User-ID oder BotProfile.id
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_ollama_dict(self) -> Dict[str, str]:
        """Konvertiert das Objekt in das Format, das Ollama erwartet."""
        return {"role": self.role, "content": self.content}


@dataclass
class ChatSession:
    """Ein ganzer Chat-Verlauf."""
    id: UUID = field(default_factory=uuid4)
    title: str = "Neuer Chat"
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def update_title_from_content(self) -> bool:
        """
        Setzt den Titel basierend auf der ersten Nachricht.
        Gibt True zurück, wenn sich der Titel geändert hat.
        """
        if self.messages and self.title == "Neuer Chat":
            first_msg = self.messages[0].content.strip()
            if not first_msg:
                return False

            # Nimm die erste Zeile oder die ersten 30 Zeichen
            clean_title = first_msg.split('\n')[0][:30]
            if len(first_msg) > 30:
                clean_title += "..."

            self.title = clean_title
            return True
        return False