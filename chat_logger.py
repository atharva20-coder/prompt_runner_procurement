"""ChatLogger - Saves terminal chat sessions to log files."""

import io
import json
import os
import re
import sys
from datetime import datetime


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes (colors, formatting) from text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


class _TeeStream:
    """Wraps stdout to write to both the terminal and an in-memory buffer."""

    def __init__(self, original_stream: io.TextIOWrapper, buffer: io.StringIO):
        self._original = original_stream
        self._buffer = buffer

    def write(self, data: str) -> int:
        self._original.write(data)
        self._buffer.write(data)
        return len(data)

    def flush(self) -> None:
        self._original.flush()
        self._buffer.flush()

    def __getattr__(self, attr):
        return getattr(self._original, attr)


class ChatLogger:
    """Captures user/bot messages and saves them to log files.

    Creates timestamped markdown files in the `logs/` directory.
    Saves TWO files per session:
      - chat_<timestamp>_<stage>.md  — clean chat log (user/bot messages only)
      - session_<timestamp>_<stage>.log — full terminal output with all metadata
    """

    def __init__(self, log_dir: str = "logs", stage_name: str | None = None):
        self.log_dir = log_dir
        self.entries: list[dict[str, str]] = []
        self.session_start = datetime.now()
        self.stage_name = stage_name

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Start capturing stdout
        self._terminal_buffer = io.StringIO()
        self._original_stdout = sys.stdout
        sys.stdout = _TeeStream(self._original_stdout, self._terminal_buffer)

    @staticmethod
    def _extract_agent_text(raw_content: str) -> str:
        """Extract clean agent text from a response.

        If the response is structured JSON with an 'agent' field,
        return just the agent text. Otherwise return the raw content.
        """
        try:
            clean = raw_content.strip()
            # Strip markdown code fences if LLM wrapped the JSON
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
                if clean.rstrip().endswith("```"):
                    clean = clean.rstrip()[:-3].rstrip()
            data = json.loads(clean)
            return data.get("agent", raw_content)
        except (json.JSONDecodeError, TypeError):
            return raw_content

    def log_user(self, message: str) -> None:
        """Log a user message."""
        self.entries.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat(),
        })

    def log_bot(self, raw_content: str) -> None:
        """Log a bot response, extracting clean agent text."""
        self.entries.append({
            "role": "bot",
            "content": self._extract_agent_text(raw_content),
            "raw": raw_content,
            "timestamp": datetime.now().isoformat(),
        })

    def log_stage_transition(self, from_stage: str, to_stage: str) -> None:
        """Log a stage transition event."""
        self.entries.append({
            "role": "system",
            "content": f"Stage transition: {from_stage} → {to_stage}",
            "timestamp": datetime.now().isoformat(),
        })

    def save(self) -> str:
        """Save both the clean chat log and the full terminal session log.

        Returns the path of the clean chat log.
        """
        # Restore stdout before saving
        if isinstance(sys.stdout, _TeeStream):
            sys.stdout = self._original_stdout

        timestamp = self.session_start.strftime("%Y-%m-%d_%H-%M-%S")
        stage_suffix = f"_{self.stage_name}" if self.stage_name else ""

        # --- 1. Clean chat log (existing format) ---
        chat_filename = f"chat_{timestamp}{stage_suffix}.md"
        chat_filepath = os.path.join(self.log_dir, chat_filename)

        if self.entries:
            with open(chat_filepath, "w", encoding="utf-8") as f:
                f.write("# Chat Log\n\n")
                f.write(f"**Date:** {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
                if self.stage_name:
                    f.write(f"**Stage:** {self.stage_name}\n")
                f.write(f"**Messages:** {len(self.entries)}\n\n")
                f.write("---\n\n")

                for entry in self.entries:
                    if entry["role"] == "user":
                        f.write(f"**You:** {entry['content']}\n\n")
                    elif entry["role"] == "bot":
                        f.write(f"**Bot:** {entry['content']}\n")
                        if entry.get("raw") and entry["raw"] != entry["content"]:
                            f.write(f"{entry['raw']}\n")
                        f.write("\n")
                    elif entry["role"] == "system":
                        f.write(f"*{entry['content']}*\n\n")

        # --- 2. Full terminal session log ---
        session_filename = f"session_{timestamp}{stage_suffix}.log"
        session_filepath = os.path.join(self.log_dir, session_filename)

        terminal_output = self._terminal_buffer.getvalue()
        clean_output = _strip_ansi(terminal_output)

        with open(session_filepath, "w", encoding="utf-8") as f:
            f.write(f"# Full Terminal Session Log\n")
            f.write(f"Date: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if self.stage_name:
                f.write(f"Stage: {self.stage_name}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(clean_output)

        return chat_filepath

