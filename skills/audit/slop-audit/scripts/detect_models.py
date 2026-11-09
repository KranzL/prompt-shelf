#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

TOOLS = [
    ("Claude Code", [r"noreply@anthropic\.com", r"Generated with \[?Claude Code", r"Co-Authored-By:\s*Claude\b", r"\bClaude Code\b", r"claude\[bot\]"]),
    ("OpenAI Codex", [r"\bCodex\b", r"noreply@openai\.com", r"chatgpt-codex-connector", r"openai-codex"]),
    ("GitHub Copilot", [r"\bCopilot\b", r"copilot-swe-agent", r"copilot@github\.com"]),
    ("Cursor", [r"\bCursor\b", r"cursoragent", r"cursor\.com", r"Cursor Agent"]),
    ("Gemini / Jules / Antigravity", [r"\bGemini\b", r"google-labs-jules", r"\bJules\b", r"\bAntigravity\b", r"gemini-cli"]),
    ("Devin", [r"devin-ai-integration", r"\bDevin\b"]),
    ("Aider", [r"\(aider\)", r"^aider:", r"\baider\b"]),
    ("Windsurf / Cascade", [r"\bWindsurf\b", r"\bCascade\b"]),
    ("Kiro", [r"\bKiro\b"]),
    ("Amp", [r"amp@ampcode", r"\bampcode\b", r"Amp \(Sourcegraph\)"]),
    ("Cline / Roo / Kilo", [r"\bCline\b", r"\bRoo Code\b", r"\bKilo Code\b"]),
    ("Factory Droid", [r"factory-droid", r"\bDroid\b"]),
    ("OpenHands", [r"\bOpenHands\b"]),
    ("Sweep", [r"sweep-ai", r"\bSweep AI\b"]),
    ("Codegen", [r"codegen-sh", r"\bCodegen\b"]),
    ("Goose", [r"\bGoose\b"]),
    ("Replit Agent", [r"\bReplit\b"]),
    ("Lovable / Bolt / v0", [r"\bLovable\b", r"\bbolt\.new\b", r"\bv0\.dev\b"]),
    ("Zencoder", [r"\bZencoder\b"]),
    ("Augment", [r"\bAugment Code\b", r"augment-code"]),
]
TOOL_RES = [(name, [re.compile(p, re.I | re.M) for p in pats]) for name, pats in TOOLS]

MODEL_RE = re.compile(
    r"(Claude (?:Opus|Sonnet|Haiku|Fable|Mythos)(?: \d+(?:\.\d+)?)?|claude-[a-z]+-\d[\w.-]*|"
    r"gpt-\d[\w.-]*|GPT-\d(?:\.\d+)?(?:-codex|-Codex)?|\bo[134](?:-mini|-pro)?\b|"
    r"gemini-[\w.-]+|Gemini \d(?:\.\d+)?(?: (?:Pro|Flash))?|grok-[\w.-]+|Grok(?: Code)?(?: Fast)?(?: \d+)?|"
    r"deepseek-[\w.-]+|DeepSeek(?: V\d(?:\.\d+)?)?|qwen[\w.-]*|Qwen\d?[\w.-]*|kimi-[\w.-]+|Kimi K\d(?:\.\d+)?|"
    r"glm-[\w.-]+|GLM-?\d(?:\.\d+)?|Composer(?: \d)?|Devstral|Codestral|Mistral[\w.-]*|Llama[\w.-]*)",
    re.I,
)
TRAILER_LINE = re.compile(r"(?im)^(?:Co-Authored-By|Generated with|Signed-off-by|Assisted-by|Made-with|Reviewed-by|Model):?.*$")

CONFIG_FILES = [
    ("Claude Code", ["CLAUDE.md", ".claude/", "CLAUDE.local.md"]),
    ("Any agent (AGENTS.md)", ["AGENTS.md"]),
    ("Cursor", [".cursorrules", ".cursor/"]),
    ("GitHub Copilot", [".github/copilot-instructions.md", ".github/instructions/"]),
    ("Gemini", ["GEMINI.md", ".gemini/"]),
    ("Windsurf", [".windsurfrules", ".windsurf/"]),
    ("Cline / Roo", [".clinerules", ".roo/", ".roomodes"]),
    ("Kiro", [".kiro/"]),
    ("Codex", [".codex/", "codex.md"]),
    ("Aider", [".aider.conf.yml", ".aider/"]),
    ("Continue", [".continue/"]),
    ("Junie", [".junie/"]),
    ("Zed", [".zed/", ".rules"]),
    ("Devin", [".devin/"]),
    ("Amp", ["AGENT.md"]),
]


def git(root, *args):
    try:
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def analyze(root, since=None, max_commits=5000):
    args = ["log", f"--max-count={max_commits}", "--format=%H%x1f%an%x1f%ae%x1f%aI%x1f%B%x1e"]
    if since:
        args.append(f"--since={since}")
    raw = git(root, *args)
    if raw is None:
        return None
    commits = [c for c in raw.split("\x1e") if c.strip()]
    per_tool = defaultdict(lambda: {"commits": 0, "first": None, "last": None, "models": defaultdict(int), "authors": defaultdict(int)})
    total = 0
    attributed = 0
    for c in commits:
        parts = c.strip("\n").split("\x1f")
        if len(parts) < 5:
            continue
        sha, name, email, date, body = parts[0], parts[1], parts[2], parts[3], "\x1f".join(parts[4:])
        total += 1
        haystack = f"{name} <{email}>\n{body}"
        trailer_text = "\n".join(TRAILER_LINE.findall(body)) + f"\n{name} <{email}>"
        matched = []
        for tool, pats in TOOL_RES:
            if any(p.search(haystack) for p in pats):
                matched.append(tool)
        if not matched:
            continue
        attributed += 1
        for tool in matched:
            rec = per_tool[tool]
            rec["commits"] += 1
            rec["authors"][f"{name} <{email}>"] += 1
            d = date[:10]
            rec["first"] = d if rec["first"] is None or d < rec["first"] else rec["first"]
            rec["last"] = d if rec["last"] is None or d > rec["last"] else rec["last"]
            for m in MODEL_RE.finditer(trailer_text):
                rec["models"][m.group(1).strip()] += 1
    configs = []
    for tool, paths in CONFIG_FILES:
        present = [p for p in paths if os.path.exists(os.path.join(root, p))]
        if present:
            configs.append({"tool": tool, "paths": present})
    return {
        "root": root,
        "commits_scanned": total,
        "commits_attributed": attributed,
        "tools": {
            t: {
                "commits": r["commits"],
                "share": round(r["commits"] / total, 3) if total else 0,
                "first": r["first"],
                "last": r["last"],
                "models": dict(sorted(r["models"].items(), key=lambda kv: -kv[1])),
                "authors": dict(sorted(r["authors"].items(), key=lambda kv: -kv[1])[:5]),
            }
            for t, r in sorted(per_tool.items(), key=lambda kv: -kv[1]["commits"])
        },
        "config_files": configs,
    }


def render(result):
    if result is None:
        return "Not a git repository (or git is unavailable). Ask the user which tools and models wrote this code."
    lines = [f"# Which agents touched {result['root']}", ""]
    lines.append(f"Commits scanned: {result['commits_scanned']}. Attributed to an agent by trailer or author: {result['commits_attributed']}.")
    lines.append("")
    if result["tools"]:
        lines.append("| tool | commits | share | first | last | models named in trailers |")
        lines.append("|---|---:|---:|---|---|---|")
        for t, r in result["tools"].items():
            models = ", ".join(f"{m} ({n})" for m, n in list(r["models"].items())[:4]) or "none named"
            lines.append(f"| {t} | {r['commits']} | {r['share']:.0%} | {r['first']} | {r['last']} | {models} |")
    else:
        lines.append("No agent trailers found. Attribution relies on the user's account of which tools were used.")
    lines.append("")
    if result["config_files"]:
        lines.append("Agent config files present: " + "; ".join(f"{c['tool']} ({', '.join(c['paths'])})" for c in result["config_files"]))
    else:
        lines.append("No agent config files (CLAUDE.md, AGENTS.md, .cursorrules, ...) found.")
    lines.append("")
    lines.append("Commits without a trailer may still be agent-written. Treat this as a floor, not a census.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Infer which coding agents and models touched a repo from commit trailers and config files.")
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--since", help="git --since value, e.g. 2026-01-01 or '6 months ago'")
    ap.add_argument("--max-commits", type=int, default=5000)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.path)
    result = analyze(root, args.since, args.max_commits)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render(result))


if __name__ == "__main__":
    main()
