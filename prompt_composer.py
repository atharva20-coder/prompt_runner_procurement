"""Prompt Composer - Runtime prompt templating with customer data injection."""

import json
import re
from datetime import datetime
from pathlib import Path


def _substitute_placeholders(template: str, data: dict) -> str:
    """Replace {key} placeholders in template, but ONLY for keys present in data.

    Unlike str.format_map(), this ignores any {…} sequences that aren't
    simple known keys — so JSON examples, format specs, and nested braces
    in prompts are left untouched.
    """

    def _replacer(match: re.Match) -> str:
        key = match.group(1)
        if key in data:
            return str(data[key])
        return match.group(0)  # leave unknown placeholders as-is

    # Match {word_characters} but not {{ or }}
    return re.sub(r"\{(\w+)\}", _replacer, template)


class PromptComposer:
    """Composes stage prompts by injecting customer data and handoff context."""

    def __init__(self, scripts_dir: str, customer_data: dict):
        self.scripts_dir = Path(scripts_dir)
        self.customer_data = customer_data

    def compose(
        self,
        prompt_file: str,
        handoff_data: dict | None = None,
        modules: list[str] | None = None,
    ) -> str:
        """Load a prompt template, inject customer data, and append handoff context.

        Args:
            prompt_file: Filename of the prompt template in scripts_dir.
            handoff_data: Optional dict from the previous stage's next_stage tool.
            modules: Optional list of module file paths (relative to scripts_dir).
                     When provided, modules are assembled in order instead of
                     reading the single prompt_file.

        Returns:
            The fully composed prompt string.
        """
        template = self._load_template(prompt_file, modules)

        # Support inline include directives when modules are not provided.
        # Lines of the form: <<include: relative/path/to/file.md>>
        # will be replaced with the contents of that file from scripts_dir.
        def _expand_includes(text: str) -> str:
            lines: list[str] = []
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("<<include:") and stripped.endswith(">>"):
                    include_path = stripped[len("<<include:"): -2].strip()
                    path = self.scripts_dir / include_path
                    if not path.exists():
                        # Keep the original line if file not found
                        lines.append(line)
                        continue
                    with open(path, "r", encoding="utf-8") as f:
                        lines.append(f.read())
                else:
                    lines.append(line)
            return "\n".join(lines)

        if not modules:
            template = _expand_includes(template)
            terminator = "## END OF MODULE IMPORTS"
            if terminator in template:
                template = template.split(terminator, 1)[0]

        # Build the data dict: customer data + runtime values
        now = datetime.now()
        data = {
            **self.customer_data,
            "current_date": now.strftime("%d-%m-%Y"),
            "current_time": now.strftime("%I:%M %p"),
        }

        # Inject known placeholders only (safe for JSON/code blocks in prompts)
        prompt = _substitute_placeholders(template, data)

        # Append handoff context from previous stage
        if handoff_data:
            context_json = json.dumps(handoff_data, indent=2, ensure_ascii=False)
            prompt += (
                f"\n\n## CONTEXT FROM PREVIOUS STAGE\n"
                f"```json\n{context_json}\n```"
            )

        return prompt

    def _load_template(
        self,
        prompt_file: str,
        modules: list[str] | None = None,
    ) -> str:
        """Load a prompt template from modules or a single file.

        When modules are provided, each module file is read and concatenated
        in the specified order, separated by newlines. This is the assembled
        prompt that gets sent to the LLM — no single-file fallback is needed.

        When modules are NOT provided, falls back to reading prompt_file directly.
        """
        if modules:
            parts: list[str] = []
            for module_path in modules:
                path = self.scripts_dir / module_path
                if not path.exists():
                    raise FileNotFoundError(
                        f"Prompt module not found: {path}"
                    )
                with open(path, "r", encoding="utf-8") as f:
                    parts.append(f.read())
            return "\n".join(parts)

        # Fallback: single-file prompt (used by non-modular stages)
        path = self.scripts_dir / prompt_file
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()
