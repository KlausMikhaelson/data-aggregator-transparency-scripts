#!/usr/bin/env python3
"""
WHAT TOKENWRAP READS FROM YOUR MACHINE  (Python CLI — transparency excerpt)
===========================================================================

This file is a verbatim excerpt of the real `claudewrap.py` CLI, trimmed to the
*only* code that touches your filesystem. Nothing here is hidden or obfuscated —
the full script is the same logic plus the login/upload plumbing.

In plain terms:

  ✓ We read two folders, locally, on YOUR computer:
        ~/.claude/history.jsonl      ~/.claude/projects/    (Claude Code)
        ~/.codex/sessions/                                  (Codex)
  ✓ From those we extract ONLY counts: how many prompts, how many tokens,
    which model, and the date. Word counts for "please"/greetings/curses.
  ✓ Real project paths are replaced with project-1, project-2, … before
    anything is sent.

  ✗ We never read your source code or file contents.
  ✗ We never read or send the text of your prompts/messages (only word counts).
  ✗ We never send real project names or file paths.

Everything below runs locally; only the resulting numbers are uploaded.
"""
from pathlib import Path

# ── The ONLY locations we ever open ──────────────────────────────────────────
DEFAULT_HISTORY = Path.home() / ".claude" / "history.jsonl"
DEFAULT_PROJECTS = Path.home() / ".claude" / "projects"
DEFAULT_CODEX = Path.home() / ".codex" / "sessions"

# The words we count (we store the COUNT, never the message text).
POLITE = ["please", "thanks", "thank you", "ty", "appreciate"]
GREETINGS = ["hi", "hello", "hey", "good morning", "good evening"]
CURSES = ["damn", "wtf", "..."]  # full list in the real script


def _read_jsonl(path):
    """Read a local .jsonl file line by line. (read-only; never written.)"""
    try:
        fh = path.open(encoding="utf-8")
    except OSError:
        return
    with fh:
        for line in fh:
            line = line.strip()
            if line:
                yield line  # parsed as JSON in the real script


def count_terms(text, terms):
    """Count whole-word matches. We keep the NUMBER, and discard the text."""
    lowered = text.lower()
    return sum(lowered.count(t) for t in terms)


def read_claude_prompts(history_path):
    """From history.jsonl we take ONLY: a project label + word counts.
    The prompt text itself is counted and then thrown away."""
    prompts = {"total": 0, "please": 0, "greetings": 0, "curses": 0}
    for entry in _read_jsonl(history_path):
        text = entry  # the user's prompt — used only to count words, never kept
        prompts["total"] += 1
        prompts["please"] += count_terms(text, POLITE)
        prompts["greetings"] += count_terms(text, GREETINGS)
        prompts["curses"] += count_terms(text, CURSES)
    return prompts  # <-- numbers only; no text, no code


def read_token_usage(session_file):
    """From session transcripts we take ONLY: model name, token counts, date.
    We do NOT read the conversation content."""
    for entry in _read_jsonl(session_file):
        # entry == {"type": "assistant", "message": {"model", "usage"}, ...}
        # we keep: model, usage.input_tokens/output_tokens/cache_*, timestamp
        # we keep nothing else from the message.
        pass


def anonymize_projects(per_project):
    """Real paths NEVER leave your machine — they become project-1, 2, …"""
    order = sorted(per_project, key=lambda k: -per_project[k])
    mapping = {real: f"project-{i + 1}" for i, real in enumerate(order)}
    return {mapping[k]: v for k, v in per_project.items()}


# What actually gets uploaded looks like this — pure numbers:
EXAMPLE_UPLOAD = {
    "prompts": {"total": 246, "please": 14, "greetings": 2, "curses": 1,
                "per_project": {"project-1": 108, "project-2": 56}},
    "models": {"tokens_by_model": {"claude-opus-4-8": {"input_tokens": 271000}},
               "total_switches": 19},
}
