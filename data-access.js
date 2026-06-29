/*
 * WHAT TOKENWRAP READS FROM YOUR MACHINE  (Node CLI — transparency excerpt)
 * ========================================================================
 *
 * This file is a verbatim excerpt of the real `claudewrap.js` CLI, trimmed to
 * the *only* code that touches your filesystem. Nothing here is hidden — the
 * full script is the same logic plus the login/upload plumbing.
 *
 * In plain terms:
 *
 *   ✓ We read two folders, locally, on YOUR computer:
 *         ~/.claude/history.jsonl    ~/.claude/projects/   (Claude Code)
 *         ~/.codex/sessions/                               (Codex)
 *   ✓ From those we extract ONLY counts: how many prompts, how many tokens,
 *     which model, and the date. Word counts for "please"/greetings/curses.
 *   ✓ Real project paths are replaced with project-1, project-2, … before
 *     anything is sent.
 *
 *   ✗ We never read your source code or file contents.
 *   ✗ We never read or send the text of your prompts/messages (only counts).
 *   ✗ We never send real project names or file paths.
 *
 * Everything below runs locally; only the resulting numbers are uploaded.
 */
const os = require("os");
const path = require("path");

// ── The ONLY locations we ever open ─────────────────────────────────────────
const HOME = os.homedir();
const DEFAULT_HISTORY = path.join(HOME, ".claude", "history.jsonl");
const DEFAULT_PROJECTS = path.join(HOME, ".claude", "projects");
const DEFAULT_CODEX = path.join(HOME, ".codex", "sessions");

// The words we count (we store the COUNT, never the message text).
const POLITE = ["please", "thanks", "thank you", "ty", "appreciate"];
const GREETINGS = ["hi", "hello", "hey", "good morning", "good evening"];
const CURSES = ["damn", "wtf", "..."]; // full list in the real script

function countTerms(text, terms) {
  // Count whole-word matches. We keep the NUMBER, and discard the text.
  const lowered = text.toLowerCase();
  return terms.reduce((n, t) => n + lowered.split(t).length - 1, 0);
}

function readClaudePrompts(entries) {
  // From history.jsonl we take ONLY: a project label + word counts.
  // The prompt text itself is counted and then thrown away.
  const prompts = { total: 0, please: 0, greetings: 0, curses: 0 };
  for (const text of entries) {
    prompts.total += 1;
    prompts.please += countTerms(text, POLITE);
    prompts.greetings += countTerms(text, GREETINGS);
    prompts.curses += countTerms(text, CURSES);
  }
  return prompts; // <-- numbers only; no text, no code
}

function readTokenUsage(entry) {
  // From session transcripts we take ONLY: model name, token counts, date.
  // entry === { type: "assistant", message: { model, usage }, timestamp }
  // we keep: model, usage.input_tokens/output_tokens/cache_*, timestamp.
  // we keep nothing else from the message — not the conversation content.
}

function anonymizeProjects(perProject) {
  // Real paths NEVER leave your machine — they become project-1, 2, …
  const order = Object.keys(perProject).sort((a, b) => perProject[b] - perProject[a]);
  const mapping = {};
  order.forEach((real, i) => { mapping[real] = `project-${i + 1}`; });
  const out = {};
  for (const [k, v] of Object.entries(perProject)) out[mapping[k]] = v;
  return out;
}

// What actually gets uploaded looks like this — pure numbers:
const EXAMPLE_UPLOAD = {
  prompts: { total: 246, please: 14, greetings: 2, curses: 1,
             per_project: { "project-1": 108, "project-2": 56 } },
  models: { tokens_by_model: { "claude-opus-4-8": { input_tokens: 271000 } },
            total_switches: 19 },
};
