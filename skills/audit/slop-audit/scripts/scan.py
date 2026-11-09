#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from collections import defaultdict

CODE_EXT = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte",
    ".py", ".go", ".rs", ".java", ".kt", ".kts", ".scala", ".cs",
    ".rb", ".swift", ".php", ".dart", ".ex", ".exs",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".m", ".mm",
}
DOC_EXT = {".md", ".mdx", ".rst", ".txt"}
JS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte"}
TS_LIKE = {".ts", ".tsx"}
PY = {".py"}
GO = {".go"}
RS = {".rs"}
JVM = {".java", ".kt", ".kts", ".scala", ".cs"}
RB = {".rb"}
SWIFT = {".swift"}
PHP = {".php"}
DART = {".dart"}
BRACE = JS | GO | RS | JVM | SWIFT | PHP | DART | {".c", ".cc", ".cpp", ".h", ".hpp", ".m", ".mm"}

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", "out", ".next", ".nuxt", "vendor",
    "target", "__pycache__", ".venv", "venv", "env", "coverage", ".turbo",
    ".cache", ".idea", ".vscode", "Pods", "DerivedData", ".gradle", "bin", "obj",
    ".svelte-kit", ".output", ".parcel-cache", "generated", "__generated__",
    ".dart_tool", "deps", "_build", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".tox", "site-packages", ".terraform", "migrations",
}
GENERATED = re.compile(
    r"(\.min\.|\.generated\.|\.pb\.|_pb2\.|\.d\.ts$|\.lock$|-lock\.|\.snap$|\.map$|"
    r"\.g\.dart$|\.freezed\.dart$|\.gen\.(go|ts)$|_generated\.|\.generated/|schema\.prisma$)"
)
TESTISH = re.compile(
    r"(\.test\.|\.spec\.|_test\.|_spec\.|/tests?/|/__tests__/|/spec/|/testing/|"
    r"/fixtures?/|/__mocks__/|/mocks?/|conftest\.py|(^|/)test_\w+\.py$|/e2e/|/cypress/|/playwright/)"
)
CONFIGISH = re.compile(
    r"(cli|/bin/|scripts?/|logger|logging|/log/|\.config\.|vite|webpack|rollup|esbuild|eslint|"
    r"prettier|jest|vitest|playwright|cypress|storybook|tailwind|postcss|next\.config|nuxt\.config|"
    r"svelte\.config|astro\.config|seed|migrat|tooling|tools?/|examples?/|benchmarks?/|__main__|manage\.py|setup\.py)"
)

PATTERNS = {
    "implicit-state-machine": ("Implicit state machine", "high", "Boolean flags or nullable values that together encode one state nobody named"),
    "swallowed-errors": ("Swallowed errors", "high", "Catch or except blocks that drop, log-and-continue, or return a default"),
    "silent-fallbacks": ("Silent fallbacks", "high", "Mock data, sentinel defaults, or fallback branches that hide a failure"),
    "test-weakening": ("Weakened tests", "high", "Skipped, vacuous, assertion-free, or mock-everything tests"),
    "phantom-apis": ("Phantom imports", "high", "Imports of packages not declared in the project's dependency manifest"),
    "defensive-overkill": ("Defensive overkill", "medium", "Guards for states the types already rule out"),
    "type-escape-hatches": ("Type escape hatches", "medium", "Casts, ignores, and lint disables that silence the compiler"),
    "compat-shims": ("Compat shims", "medium", "Aliases, re-exports, and deprecated wrappers kept for callers that do not exist"),
    "duplicate-helpers": ("Duplicate helpers", "medium", "The same helper defined in more than one file"),
    "over-abstraction": ("Over-abstraction", "medium", "Managers, wrappers, factories, barrels, and forwarding functions with one caller"),
    "god-files": ("God files", "medium", "Very long files, very long functions, deep nesting"),
    "stringly-typed": ("Stringly typed state", "medium", "Status strings compared as raw literals across files"),
    "boolean-params": ("Boolean parameters", "medium", "Functions and props with several booleans that should be one union"),
    "react-smells": ("React smells", "medium", "Effects as events, derived state in effects, silenced deps, index keys"),
    "async-misuse": ("Async misuse", "medium", "Await in loops, async forEach, sleep as synchronization, mixed styles"),
    "hardcoded-config": ("Hardcoded config", "medium", "Localhost URLs, secrets, magic delays"),
    "performance-waste": ("Performance waste", "medium", "N+1 queries, repeated passes, linear search in loops, logging and regex in hot loops"),
    "stub-code": ("Stub code", "low", "TODOs, placeholders, simplified-for-now comments, empty bodies"),
    "restating-comments": ("Restating comments", "low", "Comments that repeat the next line, banners, narration"),
    "leftover-debug": ("Leftover debug", "low", "console.log, print, debugger, conflict markers"),
    "dead-code": ("Dead code", "low", "Commented-out code, if (false), unused markers"),
    "generic-naming": ("Generic naming", "low", "processData, result2, utils.ts, helpers.ts"),
    "stray-files": ("Stray files", "low", "Summary docs, backups, scratch scripts left in the repo"),
    "emoji-and-hype": ("Emoji and hype", "low", "Emoji in code or docs, marketing words in comments and READMEs"),
}
SEMANTIC_ONLY = {
    "duplicated-truth": "The same fact stored in two places that can drift apart",
    "scope-drift": "Commits whose diff reaches far beyond their message; needs git history",
    "false-screens": "UI that can show success, done, or empty when the data says otherwise",
}
SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}


def sig(pattern, regex, note, langs=None, scope="code", flags=re.M, check=None):
    return {
        "pattern": pattern,
        "re": re.compile(regex, flags),
        "note": note,
        "langs": langs,
        "scope": scope,
        "check": check,
    }


def alias_differs(m):
    return m.group(1) != m.group(2)


def not_cas(m):
    return not re.search(r"(?i)compareandswap|compareandset|compare_exchange|^cas$", m.group(1))


def not_skeleton(m):
    before = m.string[max(0, m.start() - 300): m.start()]
    return not re.search(r"(?i)skeleton|placeholder|Array\.from\(|Array\(\s*\d|\[\.\.\.Array\(", before)


INDEPENDENT_TOGGLE = re.compile(r"(?i)(open|visible|expanded|collapsed|hover|focus|menu|modal|dialog|drawer|dropdown|tooltip|sidebar|checked|selected|pinned|muted|dark|mounted)")


GENERATED_HEAD = re.compile(r"(?i)@generated|code generated|do not edit|auto-?generated|automatically generated")


def looks_generated(text):
    if GENERATED_HEAD.search(text[:600]):
        return True
    longest = max((len(l) for l in text.split("\n")), default=0)
    return longest > 1000


ENV_DEFAULT = r"""['"](?!\d+['"]|development|production|test|info|debug|warn|error|true|false|utf-?8|localhost['"])[^'"]{2,}['"]"""

HYPE = (
    r"\b(?:comprehensive|robust|seamless(?:ly)?|production[- ]ready|enterprise[- ]grade|"
    r"battle[- ]tested|cutting[- ]edge|state[- ]of[- ]the[- ]art|leverag(?:e|es|ing)|"
    r"blazing(?:ly)?[- ]fast|effortless(?:ly)?|world[- ]class|best[- ]in[- ]class|"
    r"elegant(?:ly)?|powerful|full[- ]featured|fully[- ]featured|highly (?:scalable|performant|optimized))\b"
)
EMOJI = (
    r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2B55\u231A\u231B\u23E9-\u23FA\U0001F000-\U0001F2FF]|"
    r"\\u\{?(?:1F[0-9A-Fa-f]{3}|2[67][0-9A-Fa-f]{2}|2B50|2705|274C)\}?|\\U0001F[0-9A-Fa-f]{3}|&#x1F[0-9A-Fa-f]{3};"
)

SIGNALS = [
    sig("swallowed-errors", r"catch\s*(?:\([^)]*\))?\s*\{\s*(?://[^\n]*\s*)*\}", "empty catch block", JS | JVM | SWIFT | PHP | DART),
    sig("swallowed-errors", r"catch\s*\(\s*\w+(?:\s*:\s*\w+)?\s*\)\s*\{\s*(?:console\.(?:log|error|warn|debug|info)|logger\.\w+|log\.\w+)\([^\n]*\)\s*;?\s*\}", "catch that only logs and continues", JS | JVM | DART),
    sig("swallowed-errors", r"""catch\s*(?:\([^)]*\))?\s*\{\s*return\s+(?:null|undefined|\[\]|\{\}|false|0|''|"")\s*;?\s*\}""", "catch that returns a default", JS | JVM | PHP | DART),
    sig("swallowed-errors", r"\.catch\(\s*(?:\(\s*\w*\s*\)|\w+)\s*=>\s*(?:\{\s*\}|null|undefined|false|\[\]|\{\})\s*\)|\.catch\(\s*noop\s*\)", "promise rejection discarded", JS),
    sig("swallowed-errors", r"catch\s*\(\s*(?:Exception|Throwable|Error)\s+\w+\s*\)", "broad catch; confirm it rethrows or handles", JVM),
    sig("swallowed-errors", r"catch\s*\([^)]*\)\s*\{\s*\w+\.printStackTrace\(\);?\s*\}", "catch that only prints the stack trace", JVM),
    sig("swallowed-errors", r"^\s*except\s*:\s*$", "bare except", PY),
    sig("swallowed-errors", r"^\s*except\s+(?:Exception|BaseException)\b[^\n]*:\s*$", "broad except; confirm it rethrows or handles", PY),
    sig("swallowed-errors", r"""^\s*except\b[^\n]*:\s*\n\s*(?:pass|\.\.\.|continue|return(?:\s+(?:None|\[\]|\{\}|False|0|''|""))?)\s*$""", "except that swallows", PY),
    sig("swallowed-errors", r"if\s+err\s*!=\s*nil\s*\{\s*\n\s*(?:return\s+nil|continue|break)\s*\n\s*\}", "error dropped", GO),
    sig("swallowed-errors", r"if\s+err\s*!=\s*nil\s*\{\s*\n\s*(?:log|fmt|logger|slog|zap|logrus)\.(?!Fatal|Panic)\w+\([^\n]*\)\s*\n\s*\}", "error logged and ignored", GO),
    sig("swallowed-errors", r"^\s*_\s*=\s*[\w.]+\(", "return value discarded with _", GO),
    sig("swallowed-errors", r"\.ok\(\)\s*;", "Result discarded with .ok()", RS),
    sig("swallowed-errors", r"let\s+_\s*=\s*[\w:.]+\([^\n]*\)\s*;", "Result discarded with let _", RS),
    sig("swallowed-errors", r"Err\(_\)\s*=>\s*(?:\{\s*\}|\(\))", "Err arm does nothing", RS),
    sig("swallowed-errors", r"^\s*rescue\b[^\n]*\n\s*(?:nil|end|next|return(?:\s+nil)?)\s*$", "rescue that swallows", RB),
    sig("swallowed-errors", r"\btry\?\s", "try? discards the error", SWIFT),

    sig("silent-fallbacks", r"""(?:\|\||\?\?)\s*['"](?:unknown|Unknown|UNKNOWN|N/A|n/a|default|none|None|placeholder|TBD)['"]""", "sentinel default masks a missing value", JS | PY),
    sig("silent-fallbacks", r"\b(?:mock|fake|dummy|stub)[A-Z_]\w*\b|\b(?:MOCK|FAKE|DUMMY|PLACEHOLDER|STUB)_\w+", "mock-shaped identifier in production code"),
    sig("silent-fallbacks", r"(?i)\bfall(?:s|ing)?[ -]?back\b", "fallback: name the failure it hides"),
    sig("silent-fallbacks", r"process\.env\.\w+\s*(?:\|\||\?\?)\s*" + ENV_DEFAULT, "env var with a hardcoded default", JS),
    sig("silent-fallbacks", r"""os\.(?:getenv|environ\.get)\(\s*['"]\w+['"]\s*,\s*""" + ENV_DEFAULT + r"\s*\)", "env var with a hardcoded default", PY),
    sig("silent-fallbacks", r"""(\w+)\s*:?=\s*os\.Getenv\([^)]*\)\s*\n\s*if\s+\1\s*==\s*""\s*\{\s*\n\s*\1\s*=\s*"[^"]+\"""", "env var with a hardcoded default", GO),
    sig("silent-fallbacks", r"""return\s+(?:\[\]|\{\}|null|None|nil|false|False|0|''|"")\s*;?\s*(?://|#)\s*(?i:fallback|default|ignore|safe|just in case|shouldn'?t happen|should never)""", "sentinel return with an excuse comment"),
    sig("silent-fallbacks", r"unwrap_or_default\(\)", "unwrap_or_default hides a missing value", RS),
    sig("silent-fallbacks", r"(?i)^\s*(?://|#|\*)\s*(?:fallback|fall back|graceful(?:ly)? degrad|degrade gracefully|use (?:default|mock|sample|cached) (?:data|value|response) (?:if|when))", "fallback comment"),

    sig("defensive-overkill", r"""typeof\s+\w+\s*!==?\s*['"]undefined['"]""", "typeof undefined check; use the type or optional chaining", JS),
    sig("defensive-overkill", r"\b(\w+)\s*!==?\s*(?:null|undefined)\s*&&\s*\1\s*!==?\s*(?:null|undefined)", "double null/undefined check; use != null", JS),
    sig("defensive-overkill", r"\b(\w+)\s*&&\s*\1\.\w+\s*&&\s*\1\.\w+\.\w+", "manual chaining three deep", JS),
    sig("defensive-overkill", r"\?\.\w+(?:\?\.\w+){2,}", "optional chaining three deep; the type should rule these out", JS | SWIFT | DART | {".kt", ".cs"}),
    sig("defensive-overkill", r"Array\.isArray\((\w+)\)\s*\?\s*\1\s*:\s*\[\]", "isArray-or-empty; fix the type instead", JS),
    sig("defensive-overkill", r"""\b(\w+)\s*\?\s*\1\s*:\s*(?:\[\]|\{\}|''|""|null|undefined|0)\b""", "x ? x : default", JS),
    sig("defensive-overkill", r"JSON\.parse\(JSON\.stringify\(", "deep clone hack; use structuredClone", JS),
    sig("defensive-overkill", r"(?i)^\s*(?://|#|\*)\s*(?:defensive(?:ly)?|just in case|safety check|sanity check|guard against|should never happen|shouldn'?t happen|this should not happen|extra (?:safety|check))\b", "defensive comment"),
    sig("defensive-overkill", r"isinstance\(\s*\w+\s*,\s*(?:str|int|float|bool|list|dict|tuple)\s*\)\s+(?:and|or)\s+isinstance\(", "type sniffing; use types", PY),
    sig("defensive-overkill", r"if\s+\w+\s+is\s+not\s+None\s+and\s+\w+\s+is\s+not\s+None\s+and\s+\w+\s+is\s+not\s+None", "triple None check", PY),

    sig("type-escape-hatches", r"\bas\s+any\b", "as any", TS_LIKE),
    sig("type-escape-hatches", r"\bas\s+unknown\s+as\b", "as unknown as", TS_LIKE),
    sig("type-escape-hatches", r"<any>\s*\w", "angle-bracket any cast", TS_LIKE),
    sig("type-escape-hatches", r":\s*any\b(?!\w)", "any annotation", TS_LIKE),
    sig("type-escape-hatches", r"Record<string,\s*any>", "Record<string, any>", TS_LIKE),
    sig("type-escape-hatches", r"@ts-ignore|@ts-nocheck", "ts-ignore", TS_LIKE),
    sig("type-escape-hatches", r"@ts-expect-error\s*$", "ts-expect-error without a reason", TS_LIKE),
    sig("type-escape-hatches", r"eslint-disable(?:-next-line|-line)?\b", "eslint disable", JS),
    sig("type-escape-hatches", r"[\w\])]!(?=[.;,)\]]|\s*$)", "non-null assertion", TS_LIKE | DART | SWIFT),
    sig("type-escape-hatches", r"\w!!", "Kotlin !! assertion", {".kt", ".kts"}),
    sig("type-escape-hatches", r"#\s*type:\s*ignore|#\s*pyright:\s*ignore|#\s*mypy:\s*ignore", "type ignore", PY),
    sig("type-escape-hatches", r"(?::\s*|->\s*)Any\b", "Any annotation", PY),
    sig("type-escape-hatches", r"#\s*noqa(?!:)|#\s*pylint:\s*disable", "lint disable without a code", PY),
    sig("type-escape-hatches", r"interface\{\}", "empty interface; use a concrete type or generic", GO),
    sig("type-escape-hatches", r"//\s*nolint\b", "nolint", GO),
    sig("type-escape-hatches", r"#\[allow\(", "allow attribute", RS),
    sig("type-escape-hatches", r"@SuppressWarnings\(|#pragma\s+warning\s+disable|@SuppressLint\(", "warning suppression", JVM),
    sig("type-escape-hatches", r"\bas\s+dynamic\b|\bdynamic\s+\w+\s*=", "dynamic typing escape", {".cs", ".dart"}),

    sig("compat-shims", r"(?i)\bbackwards?[ -]?compat(?:ible|ibility)?\b|\bfor compat(?:ibility)?\b", "backwards-compat excuse"),
    sig("compat-shims", r"(?i)\b(?:kept|keep|keeping|retain(?:ed|ing)?|preserv(?:e|ed|ing)|left|leaving)\b[^\n]{0,40}\b(?:for|to)\b[^\n]{0,30}\b(?:compat|legacy|existing (?:callers|users|code|consumers)|old (?:callers|code|api|clients|behaviou?r)|backward)", "kept-for-compat comment"),
    sig("compat-shims", r"(?i)^\s*(?://|#|\*)\s*(?:legacy|deprecated|old (?:version|implementation|api)|remove (?:this |me )?(?:after|once|when|in)|to be removed|temporary (?:shim|wrapper|alias)|alias for)\b", "legacy or removal comment"),
    sig("compat-shims", r"@deprecated\b|@Deprecated\b|\[Obsolete|#\[deprecated|DeprecationWarning\b", "deprecated marker: delete if no callers remain"),
    sig("compat-shims", r"^\s*export\s+(?:const|let|var)\s+(\w+)\s*=\s*(\w+)\s*;?\s*$", "alias export", JS, check=alias_differs),
    sig("compat-shims", r"^\s*export\s*\{\s*\w+\s+as\s+\w+\s*\}", "renamed re-export", JS),
    sig("compat-shims", r"^(\w+)\s*=\s*(\w+)\s*#\s*[^\n]*(?i:alias|compat|backward|legacy|old|deprecated)", "alias with compat comment", PY, check=alias_differs),
    sig("compat-shims", r"\b\w+(?:Legacy|Deprecated|Compat|Shim|Polyfill)\b\s*[=(:]|\b(?:legacy|deprecated|old|compat|shim)_\w+\s*[=(:]", "legacy-named symbol"),
    sig("compat-shims", r"\b\w+(?:V2|V3|_v2|_v3)\b\s*[=(:]", "versioned symbol name; is the old one still used"),

    sig("stub-code", r"\b(?:TODO|FIXME|XXX|HACK)\b", "todo marker"),
    sig("stub-code", r"(?i)\bfor now\b", "for now"),
    sig("stub-code", r"(?i)\bsimplified\b", "simplified"),
    sig("stub-code", r"(?i)\bin a real (?:implementation|app|application|system|world|scenario|project|deployment)\b", "in a real implementation"),
    sig("stub-code", r"(?i)\bin production,?\s+(?:you|this|we|it) (?:would|should|could)\b", "in production you would"),
    sig("stub-code", r"""(?i)\bplaceholder\b(?!\s*[=:"'])""", "placeholder"),
    sig("stub-code", r"(?i)\bnot (?:yet )?implemented\b|NotImplementedError|unimplemented!\(|todo!\(", "not implemented"),
    sig("stub-code", r"(?i)\bstub(?:bed|s)?\b|\bdummy\b", "stub or dummy"),
    sig("stub-code", r"(?i)\bthis would (?:normally|typically|usually|ideally)\b|\bwould (?:go|be|live|happen) here\b|\b(?:actual|real) (?:implementation|logic|code) (?:goes|would go) here\b", "would-go-here comment"),
    sig("stub-code", r"(?i)\bhardcoded (?:for|to)\b|\bfor (?:demo|demonstration|testing|illustration|illustrative) purposes\b", "hardcoded for demo"),
    sig("stub-code", r"(?i)\b(?:basic|minimal|naive|simple) (?:implementation|version|example) (?:for|of|that)\b", "minimal version comment"),
    sig("stub-code", r"(?i)\bmock(?:ed)? (?:data|response|implementation|service|client|api|value|result)s?\b", "mock in production code"),
    sig("stub-code", r"""return\s+(?:null|undefined|\[\]|\{\}|0|''|""|None|nil|false|False)\s*;?\s*(?://|#)\s*(?i:todo|stub|placeholder|temp|for now|implement)""", "sentinel return marked temporary"),
    sig("stub-code", r"def\s+\w+\([^)]*\)[^\n]*:\s*\n\s*pass\s*$", "empty function body", PY),

    sig("restating-comments", r"^\s*(?://|#)\s*[=\-#*~]{6,}\s*$", "banner comment"),
    sig("restating-comments", r"^\s*(?://|#)\s*[=\-#*~]{3,}\s*[\w ]{1,40}\s*[=\-#*~]{3,}\s*$", "section banner"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Step|STEP|Phase|PHASE|Section|SECTION)\s+\d+\b", "numbered step comment"),
    sig("restating-comments", r"^\s*(?://|#)\s*Import\w*\b[^\n]*\n\s*(?:import|from|require|use|using)\b", "comment restates the import"),
    sig("restating-comments", r"^\s*(?://|#)\s*Return\w*\b[^\n]*\n\s*return\b", "comment restates the return"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Check|Validate|Verify|Ensure|Make sure)\b[^\n]*\n\s*(?:if|assert|guard|switch|match)\b", "comment restates the check"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Loop|Iterate|For each|Go through)\b[^\n]*\n\s*(?:for|while|\w+\.(?:forEach|map|filter|reduce)\b)", "comment restates the loop"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Set|Update|Initialize|Init|Assign|Store|Save|Reset)\b[^\n]*\n\s*(?:set[A-Z]\w*\(|this\.\w+\s*=|self\.\w+\s*=|\w+(?:\.\w+)*\s*=[^=])", "comment restates the assignment"),
    sig("restating-comments", r"^\s*(?://|#)\s*Exports?\b[^\n]*\n\s*export\b", "comment restates the export"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Create|Define|Declare|Build|Construct|Instantiate)\b[^\n]*\n\s*(?:const|let|var|function|class|interface|type|def|struct|enum|fn|func|val)\b", "comment restates the declaration"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Call|Invoke|Run|Execute|Trigger|Fetch|Get|Load|Send|Dispatch)\b[^\n]*\n\s*(?:(?:const|let|var)\s+[\w{}\[\], :]+\s*=\s*)?(?:await\s+)?(?:\w+\.)*\w+\(", "comment restates the call"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Increment|Decrement|Append|Push|Pop)\b[^\n]*\n\s*\w+(?:\.\w+)*\s*(?:\+\+|--|\+=|-=|\.push\(|\.append\(|\.pop\()", "comment restates the mutation"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:If|When|Otherwise|Else)\b[^\n]*\n\s*(?:if|else|elif|switch|case)\b", "comment restates the branch"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Try|Attempt)\b[^\n]*\n\s*try\b", "comment restates the try"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Log|Print|Output|Display|Show)\b[^\n]*\n\s*(?:console\.|print\(|log\.|logger\.|fmt\.)", "comment restates the log"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Wait|Sleep|Delay|Pause)\b[^\n]*\n\s*(?:await\s+)?(?:sleep|delay|wait|time\.sleep|setTimeout)\(", "comment restates the sleep"),
    sig("restating-comments", r"^\s*(?://|#)\s*(?:Let me|Let's|Now (?:we|I|let)|We (?:need|should|will|can)\b|I (?:will|'ll|need|think|believe|am going)|Wait,|Actually,|Hmm|Okay,|OK,|First,? (?:we|I|let)|Next,? (?:we|I|let)|Finally,? (?:we|I|let)|Here (?:we|I))\b", "narration comment"),
    sig("restating-comments", r"^\s*(?://|#|\*)\s*This (?:function|method|class|component|hook|file|module) (?:is|does|handles|returns|will|provides|contains)\b", "comment describes the obvious"),
    sig("restating-comments", r"/\*\*\s*\n\s*\*\s*(?:Gets?|Sets?|Returns?|Creates?|Handles?|Checks?|Updates?|Deletes?|Fetch(?:es)?|Loads?)\s+(?:the\s+|a\s+|an\s+)?[\w\s]{1,30}\.?\s*\n\s*\*/", "doc comment restates the name", JS | JVM),
    sig("restating-comments", r"@param\s+(?:\{[^}]*\}\s+)?(\w+)\s+-?\s*[Tt]he\s+\1\b", "@param restates the name", JS | JVM | PHP),
    sig("restating-comments", r'"""\s*(?:Get|Set|Return|Create|Handle|Check|Update|Delete|Fetch|Load)s?\s+(?:the\s+)?[\w\s]{1,30}\.?\s*"""', "docstring restates the name", PY),

    sig("leftover-debug", r"console\.(?:log|debug|trace|dir|table)\(", "console output; confirm it is intentional", JS),
    sig("leftover-debug", r"\bdebugger\b\s*;?\s*$", "debugger statement", JS),
    sig("leftover-debug", r"""console\.log\(\s*['"`](?:here|HERE|test|TEST|debug|DEBUG|asdf|xxx|hello|hi|foo|bar|wtf|ok|works?|a{3,}|1{3,}|123)[\s\S]{0,5}['"`]""", "debug marker log", JS),
    sig("leftover-debug", r"^\s*print\(", "print; use logging or remove", PY),
    sig("leftover-debug", r"\bpdb\.set_trace\(\)|\bbreakpoint\(\)|\bipdb\b|\bimport pdb\b", "debugger hook", PY),
    sig("leftover-debug", r"\bdbg!\(", "dbg! macro", RS),
    sig("leftover-debug", r"\bfmt\.Print(?:ln|f)?\(", "fmt.Print in library code", GO),
    sig("leftover-debug", r"System\.out\.print(?:ln)?\(|Console\.WriteLine\(", "stdout print in library code", JVM),
    sig("leftover-debug", r"binding\.pry|\bbyebug\b", "debugger hook", RB),
    sig("leftover-debug", r"var_dump\(|print_r\(|\bdd\(|\bdump\(", "debug dump", PHP),
    sig("leftover-debug", r"^(?:<{7}|>{7}|={7})(?:\s|$)", "merge conflict marker", None, "all"),

    sig("over-abstraction", r"\babstract\s+class\s+\w+|\bclass\s+(?:Abstract|Base)[A-Z]\w*\b", "abstract or base class; count the implementations", JS | JVM | PHP | DART),
    sig("over-abstraction", r"\b(?:class|interface|type|struct)\s+\w*(?:Manager|Orchestrator|Coordinator|Wrapper|Helper|Processor|Factory|Facade|Impl|Util|Utils|Strategy|Registry)\b", "pattern-named type; count the call sites"),
    sig("over-abstraction", r"@abstractmethod|from abc import", "ABC; count the implementations", PY),
    sig("over-abstraction", r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)[^{\n]*\{\s*\n\s*return\s+(?:await\s+)?(?!\1\b)\w+\([^\n]*\)\s*;?\s*\n\s*\}", "one-line forwarding function", JS),
    sig("over-abstraction", r"^\s*def\s+(\w+)\([^)]*\)[^\n]*:\s*\n\s*return\s+(?!\1\b)\w+\([^\n]*\)\s*\n", "one-line forwarding function", PY),

    sig("hardcoded-config", r"https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?::\d+)?", "localhost URL in code"),
    sig("hardcoded-config", r"""['"`](?:localhost|127\.0\.0\.1|0\.0\.0\.0):\d{2,5}['"`]""", "host:port literal in code"),
    sig("hardcoded-config", r"""(?i)\b(?:api[_-]?key|apikey|secret|password|passwd|token)\s*[:=]\s*['"][A-Za-z0-9_\-/+=]{12,}['"]""", "possible hardcoded secret"),
    sig("hardcoded-config", r"\b(?:sk|pk|rk)_(?:live|test|prod)_[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{30,}", "credential-shaped literal", None, "all"),
    sig("hardcoded-config", r"setTimeout\([^;\n]*?,\s*(\d{4,})\s*\)", "magic delay", JS),
    sig("hardcoded-config", r"time\.sleep\(\s*\d{2,}\s*\)|\bsleep\(\s*\d{4,}\s*\)", "magic sleep"),

    sig("emoji-and-hype", EMOJI, "emoji in source", None, "code"),
    sig("emoji-and-hype", EMOJI, "emoji in docs", None, "docs"),
    sig("emoji-and-hype", r"(?i)^\s*(?://|#|\*|/\*\*?|\"\"\"|''')[^\n]*" + HYPE, "marketing word in a comment", None, "code"),
    sig("emoji-and-hype", r"(?i)" + HYPE, "marketing word in docs", None, "docs"),
    sig("emoji-and-hype", r"""(?i)(?:console\.(?:log|info)|print|logger?\.(?:info|debug)|log\.(?:Printf|Println|Info))\([^\n]*\b(?:successfully|success)\b[^\n]*!""", "cheerful log message", None, "code"),

    sig("react-smells", r"useEffect\(\s*\(\)\s*=>\s*\{\s*\n\s*set[A-Z]\w*\(", "effect whose first statement sets state; derive it or move it to the event", JS),
    sig("react-smells", r"useEffect\(\s*async\b", "async effect callback", JS),
    sig("react-smells", r"eslint-disable(?:-next-line)?\s+react-hooks/exhaustive-deps", "silenced exhaustive-deps", JS),
    sig("react-smells", r"useState\(\s*props\.\w+\s*\)", "state initialized from a prop and never synced", JS),
    sig("react-smells", r"key=\{\s*(?:index|i|idx)\s*\}", "array index as key", JS, check=not_skeleton),
    sig("react-smells", r"useMemo\(\s*\(\)\s*=>\s*(?:[\w.]+|\[\]|\{\}|!\w+)\s*,", "trivial memo", JS),
    sig("react-smells", r"useCallback\(\s*\(\)\s*=>\s*\{\s*\}\s*,", "empty callback memo", JS),
    sig("react-smells", r"\bprops\.\w+\s*=[^=]", "prop mutation", JS),

    sig("async-misuse", r"\bfor\s*\((?![^)]*\bawait\b)[^)]*\)\s*\{\s*\n(?:\s*(?:const|let|var)\s+[^=\n]+=\s*)?\s*await\b", "await inside a loop; batch or Promise.all unless order matters", JS),
    sig("async-misuse", r"\.forEach\(\s*async\b", "async forEach is never awaited", JS),
    sig("async-misuse", r"new\s+Promise\(\s*async\b", "async Promise executor", JS),
    sig("async-misuse", r"await\s+new\s+Promise\(\s*(?:\(?\s*(?:r|res|resolve)\s*\)?)\s*=>\s*setTimeout\(\s*(?:r|res|resolve)\s*,\s*\d+\s*\)\s*\)", "sleep used as synchronization; what is it waiting for", JS),
    sig("async-misuse", r"^\s*for\b[^\n]*:\s*\n\s*(?:\w+\s*=\s*)?await\b", "await inside a loop; asyncio.gather unless order matters", PY),

    sig("stringly-typed", r"""\b(?:status|state|type|kind|mode|phase|step|stage|role|variant)\s*(?:===|!==|==|!=)\s*['"][\w-]+['"]""", "state compared as a raw string", None),

    sig("boolean-params", r"function\s+\w+\s*\([^)]*:\s*boolean\b[^)]*:\s*boolean\b", "two or more boolean parameters", TS_LIKE),
    sig("boolean-params", r"def\s+\w+\([^)]*:\s*bool\b[^)]*:\s*bool\b", "two or more boolean parameters", PY),
    sig("boolean-params", r"func\s+(?:\([^)]*\)\s*)?\w+\([^)]*\bbool\b[^)]*\bbool\b", "two or more boolean parameters", GO),
    sig("boolean-params", r"fn\s+\w+\([^)]*:\s*bool\b[^)]*:\s*bool\b", "two or more boolean parameters", RS),
    sig("boolean-params", r"(\w+)\([^()\n]*\b(?:true|false)\s*,\s*(?:true|false)\b", "call with consecutive boolean literals", None, check=not_cas),
    sig("boolean-params", r"(\w+)\([^()\n]*\b(?:True|False)\s*,\s*(?:True|False)\b", "call with consecutive boolean literals", PY, check=not_cas),
    sig("boolean-params", r"(\w+)\?:\s*boolean;?\s*\n\s*(\w+)\?:\s*boolean;?\s*\n\s*(\w+)\?:\s*boolean", "three optional boolean props in a row; likely a variant union", TS_LIKE),

    sig("dead-code", r"if\s*\(\s*(?:false|0)\s*\)|^\s*if\s+False\s*:|while\s*\(\s*false\s*\)", "branch that never runs"),
    sig("dead-code", r"(?i)^\s*(?://|#)\s*(?:old|previous|unused|no longer (?:used|needed)|not used|dead code|remove(?:d)? later|temporarily (?:disabled|commented))\b", "dead-code comment"),

    sig("generic-naming", r"^\s*(?:export\s+)?(?:async\s+)?function\s+(?:processData|handleData|doStuff|handleStuff|processItem|getData|fetchData|updateData|handleResponse|processResponse|doTheThing|helper|util|process|handle|manage|doWork)\s*\(", "generic function name", JS),
    sig("generic-naming", r"^\s*def\s+(?:process_data|handle_data|do_stuff|get_data|fetch_data|update_data|helper|util|process|handle|do_work|run_all|main_logic)\s*\(", "generic function name", PY),
    sig("generic-naming", r"\b(?:const|let|var)\s+(?:data|result|res|resp|item|temp|tmp|obj|val|info|thing|stuff|foo|bar|baz|payload|output|input)\d+\s*=", "numbered generic variable", JS),
    sig("generic-naming", r"^\s*(?:data|result|res|resp|item|temp|tmp|obj|val|info|thing|stuff|foo|bar|baz|payload|output)\d+\s*=", "numbered generic variable", PY),

    sig("performance-waste", r"for\s*\([^)]*\)\s*\{(?:[^{}]|\{[^{}]*\}){0,400}?(?:\bawait\s+fetch\(|\b\w+(?:\.\w+)*\.(?:query|findOne|findMany|findUnique|findFirst|findById|execute|raw|insertOne|updateOne|deleteOne|save)\()", "query inside a loop (N+1); batch it", JS),
    sig("performance-waste", r"^\s*for\b[^\n]*:\s*\n(?:[^\n]*\n){0,8}?[^\n]*\b\w+(?:\.\w+)*\.(?:execute|fetchone|fetchall|find_one|insert_one|update_one|delete_one|objects\.(?:get|filter|create|update))\(", "query inside a loop (N+1); batch it", PY),
    sig("performance-waste", r"for\s[^\n]*\{(?:[^{}]|\{[^{}]*\}){0,300}?\b\w+\.(?:Query|QueryRow|QueryContext|QueryRowContext|Exec|ExecContext)\(", "query inside a loop (N+1); batch it", GO),
    sig("performance-waste", r"\.(?:filter|map)\((?:[^()]|\([^()]*\))*\)\s*\.(?:filter|map)\((?:[^()]|\([^()]*\))*\)\s*\.(?:filter|map|reduce|forEach|some|find)\(", "three passes over one array; one loop", JS),
    sig("performance-waste", r"for\s*\((?:const|let|var)\s+\w+\s+of\s+(\w+)\)\s*\{(?:[^{}]|\{[^{}]*\}){0,300}?\b(\w+)\.(?:find|findIndex|includes|indexOf|some)\(", "linear search inside a loop; index the inner collection in a Map or Set first", JS, check=alias_differs),
    sig("performance-waste", r"^\s*for\s+\w+\s+in\s+(\w+):\s*\n(?:[^\n]*\n){0,6}?\s*if\s+\w+\s+(?:not\s+)?in\s+(\w+)\b", "membership test inside a loop; if the right side is a list make it a set", PY, check=alias_differs),
    sig("performance-waste", r"""^\s*for\b[^\n]*:\s*\n(?:[^\n]*\n){0,6}?\s*\w+\s*\+=\s*(?:f?['"]|str\()""", "string built with += in a loop; collect and join", PY),
    sig("performance-waste", r"\.insert\(\s*0\s*,", "insert at the front of a list; use collections.deque", PY),
    sig("performance-waste", r"(?i)SELECT\s+\*\s+FROM", "SELECT *; name the columns"),
    sig("performance-waste", r"for\s*\([^)]*\)\s*\{(?:[^{}]|\{[^{}]*\}){0,200}?new\s+RegExp\(", "regex built inside a loop; hoist it", JS),
    sig("performance-waste", r"^\s*for\b[^\n]*:\s*\n(?:[^\n]*\n){0,6}?\s*(?:\w+\s*=\s*)?re\.(?:compile|match|search|sub|findall|fullmatch)\(", "regex compiled inside a loop; compile once outside", PY),
    sig("performance-waste", r"(?:app|router|server)\.(?:get|post|put|patch|delete|use|all)\([^\n]*\n(?:[^\n]*\n){0,10}?[^\n]*\b(?:readFileSync|writeFileSync|execSync|readdirSync)\(", "sync IO inside a request handler", JS),
    sig("performance-waste", r"for\s*\([^)]*\)\s*\{\s*\n(?:[^\n]*\n){0,3}?\s*(?:console\.(?:log|info|debug)|logger\.(?:debug|info|log))\(", "logging inside a loop", JS),
    sig("performance-waste", r"^\s*for\b[^\n]*:\s*\n(?:[^\n]*\n){0,3}?\s*(?:print|logger\.(?:debug|info)|logging\.(?:debug|info))\(", "logging inside a loop", PY),
    sig("performance-waste", r"for\s[^\n]*\{\s*\n(?:[^\n]*\n){0,3}?\s*(?:log\.Print\w*|fmt\.Print\w*)\(", "logging inside a loop", GO),
    sig("performance-waste", r"for\s*\((?:const|let|var)\s+\w+\s+of\s+(\w+)\)\s*\{\s*\n\s*for\s*\((?:const|let|var)\s+\w+\s+of\s+\1\)", "nested loop over the same collection; quadratic", JS),
    sig("performance-waste", r"^\s*for\s+\w+\s+in\s+(\w+):\s*\n\s*for\s+\w+\s+in\s+\1:", "nested loop over the same collection; quadratic", PY),
    sig("performance-waste", r"Promise\.all\(\s*\w+\.map\(\s*(?:async\b|\(?\s*\w*\s*\)?\s*=>\s*(?:await\s+)?fetch)", "unbounded concurrency over a collection; cap it", JS),
    sig("performance-waste", r"while\s*\((?:true|!?\w+)\)\s*\{(?:[^{}]|\{[^{}]*\}){0,300}?(?:await\s+(?:sleep|delay|wait)\(|setTimeout\()", "polling loop with sleep; wait on the real signal if one exists", JS),
    sig("performance-waste", r"^\s*while\b[^\n]*:\s*\n(?:[^\n]*\n){0,8}?\s*(?:await\s+asyncio\.sleep|time\.sleep)\(", "polling loop with sleep; wait on the real signal if one exists", PY),
]

TEST_SIGNALS = [
    sig("test-weakening", r"\b(?:it|test|describe)\.skip\(|\bx(?:it|describe|test)\(|\bf(?:it|describe)\(|\b(?:it|test|describe)\.only\(|\b(?:it|test)\.todo\(", "skipped, focused, or todo test", JS, "tests"),
    sig("test-weakening", r"@pytest\.mark\.(?:skip|xfail)|pytest\.skip\(|@unittest\.skip|self\.skipTest\(", "skipped test", PY, "tests"),
    sig("test-weakening", r"\bt\.Skip\(", "skipped test", GO, "tests"),
    sig("test-weakening", r"#\[ignore\]", "ignored test", RS, "tests"),
    sig("test-weakening", r"@Ignore\b|@Disabled\b", "disabled test", JVM, "tests"),
    sig("test-weakening", r"""expect\(\s*(true|false|1|0|'[^']*'|"[^"]*")\s*\)\.(?:toBe|toEqual|toStrictEqual)\(\s*\1\s*\)|expect\(true\)\.toBeTruthy\(\)""", "vacuous assertion", JS, "tests"),
    sig("test-weakening", r"^\s*assert\s+True\b|assert\s+1\s*==\s*1\b|assertTrue\(\s*[Tt]rue\s*\)", "vacuous assertion", PY | JVM, "tests"),
    sig("test-weakening", r"assert_eq!\(\s*(\w+)\s*,\s*\1\s*\)", "vacuous assertion", RS, "tests"),
    sig("test-weakening", r"\bassert\s+true\b", "vacuous assertion", RB, "tests"),
    sig("test-weakening", r"expect\(\s*\w+\s*\)\.toBeDefined\(\)\s*;?\s*\n\s*\}\s*\)", "toBeDefined as the only real assertion", JS, "tests"),
    sig("test-weakening", r"catch\s*(?:\([^)]*\))?\s*\{\s*\n\s*(?!expect|assert|throw|fail\(|rethrow)", "try/catch inside a test can hide a failure", JS | JVM, "tests"),
    sig("test-weakening", r"^\s*except\b[^\n]*:\s*\n\s*(?:pass|assert\s+True)\s*$", "except that passes inside a test", PY, "tests"),
    sig("test-weakening", r"^\s*rescue\b[^\n]*\n\s*assert\s+true", "rescue that asserts true", RB, "tests"),
    sig("test-weakening", r"(?i)^\s*(?://|#)\s*(?:test|tests|spec)s?\s+(?:temporarily\s+)?(?:disabled|skipped|commented out|removed)\b", "disabled-test comment", None, "tests"),
]

CONFIG_SIGNALS = [
    sig("test-weakening", r"passWithNoTests|forceExit|detectOpenHandles", "test runner flag that hides failures", None, "all"),
]

STATUS_LITERAL = re.compile(r"""(?:===|!==|==|!=)\s*['"]([a-z_]{3,24})['"]""")
STATUS_STOP = {
    "string", "number", "object", "function", "undefined", "boolean", "symbol", "bigint",
    "development", "production", "test", "staging", "utf", "default", "true", "false", "null",
    "none", "left", "right", "top", "bottom", "center", "asc", "desc", "dark", "light", "ltr", "rtl",
    "win", "darwin", "linux", "main", "master", "get", "post", "put", "delete", "patch", "head",
    "options", "http", "https", "file", "data", "text", "json", "html", "css", "js", "ts",
    "px", "em", "rem", "auto", "inherit", "initial", "unset", "block", "inline", "flex", "grid",
    "button", "submit", "reset", "click", "change", "input", "keydown", "keyup", "focus", "blur",
    "enter", "escape", "tab", "space", "arrowup", "arrowdown", "arrowleft", "arrowright",
    "__proto__", "constructor", "prototype", "length", "name", "id", "key", "value", "label",
    "localhost", "utf8", "ascii", "base64", "hex", "binary", "latin1", "buffer", "unknown",
}

DEF_RES = {
    "js": [
        re.compile(r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s+(\w+)\s*\(", re.M),
        re.compile(r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*(?::[^=\n]+)?=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*(?::\s*[^=]+?)?=>", re.M),
        re.compile(r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\b", re.M),
    ],
    "py": [re.compile(r"^(?:async\s+)?def\s+(\w+)\s*\(", re.M)],
    "go": [re.compile(r"^func\s+(\w+)\s*\(", re.M)],
    "rs": [re.compile(r"^(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+(\w+)", re.M)],
}
DEF_STOP = {
    "main", "init", "setup", "teardown", "default", "run", "start", "stop", "test", "build", "new",
    "handler", "handle", "app", "page", "layout", "loader", "action", "meta", "links", "headers",
    "middleware", "config", "get", "post", "put", "delete", "patch", "head", "options",
    "generatemetadata", "getserversideprops", "getstaticprops", "getstaticpaths", "generatestaticparams",
    "render", "index", "setup_module", "teardown_module", "fixture", "register", "activate", "deactivate",
    "serve", "listen", "connect", "execute", "parse", "load", "save", "create", "update", "remove", "reset",
    "close", "open", "send", "read", "write", "up", "down", "migrate", "seed", "schema", "resolve", "reject",
}

NODE_BUILTINS = {
    "assert", "async_hooks", "buffer", "child_process", "cluster", "console", "constants", "crypto",
    "dgram", "diagnostics_channel", "dns", "domain", "events", "fs", "http", "http2", "https", "inspector",
    "module", "net", "os", "path", "perf_hooks", "process", "punycode", "querystring", "readline", "repl",
    "stream", "string_decoder", "sys", "timers", "tls", "trace_events", "tty", "url", "util", "v8", "vm",
    "wasi", "worker_threads", "zlib", "test",
}
JS_IMPORT = re.compile(r"""(?:^|\n)\s*(?:import|export)\s+(?:[^'";\n]*?\s+from\s+)?['"]([^'"\n]+)['"]|require\(\s*['"]([^'"\n]+)['"]\s*\)|import\(\s*['"]([^'"\n]+)['"]\s*\)""")
PY_IMPORT = re.compile(r"^\s*(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import)", re.M)
PY_NAME_MAP = {
    "pil": "pillow", "cv2": "opencv-python", "yaml": "pyyaml", "sklearn": "scikit-learn", "bs4": "beautifulsoup4",
    "dotenv": "python-dotenv", "jwt": "pyjwt", "dateutil": "python-dateutil", "attr": "attrs", "openssl": "pyopenssl",
    "crypto": "pycryptodome", "serial": "pyserial", "usb": "pyusb", "docx": "python-docx", "magic": "python-magic",
    "psycopg2": "psycopg2-binary", "mysqldb": "mysqlclient", "win32api": "pywin32", "gi": "pygobject", "wx": "wxpython",
    "zmq": "pyzmq", "nacl": "pynacl", "ldap": "python-ldap", "levenshtein": "python-levenshtein", "github": "pygithub",
    "jose": "python-jose", "multipart": "python-multipart", "socks": "pysocks", "telegram": "python-telegram-bot",
    "_pytest": "pytest", "google": "google", "googleapiclient": "google-api-python-client", "snowflake": "snowflake-connector-python",
    "databricks": "databricks-sdk", "fitz": "pymupdf", "markdown": "markdown", "pptx": "python-pptx", "slugify": "python-slugify",
}
PY_STDLIB = set(getattr(sys, "stdlib_module_names", set())) | {"__future__", "typing_extensions"}


def finding(pattern, path, line, note, snippet=""):
    return {"pattern": pattern, "path": path, "line": line, "note": note, "snippet": snippet.strip()[:160]}


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def snippet_at(text, pos):
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    if end == -1:
        end = len(text)
    return text[start:end]


def is_test_path(rel):
    return bool(TESTISH.search("/" + rel.replace(os.sep, "/")))


def iter_files(root, explicit=None):
    if explicit:
        for p in explicit:
            ap = p if os.path.isabs(p) else os.path.join(root, p)
            if os.path.isfile(ap):
                yield ap
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".") or d in {".github", ".claude"}]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def lang_ok(signal, ext):
    return signal["langs"] is None or ext in signal["langs"]


def run_line_signals(signals, rel, ext, text, is_test, is_doc, findings, max_per_file=40):
    per_pattern = defaultdict(int)
    for s in signals:
        if not lang_ok(s, ext):
            continue
        scope = s["scope"]
        if scope == "code" and (is_doc or is_test):
            continue
        if scope == "docs" and not is_doc:
            continue
        if scope == "tests" and not is_test:
            continue
        for m in s["re"].finditer(text):
            if s["check"] and not s["check"](m):
                continue
            if per_pattern[s["pattern"]] >= max_per_file:
                break
            per_pattern[s["pattern"]] += 1
            pos = m.start() + (len(m.group(0)) - len(m.group(0).lstrip()))
            findings.append(finding(s["pattern"], rel, line_of(text, pos), s["note"], snippet_at(text, pos)))


FLAG_RES = [
    re.compile(r"useState(?:<boolean>)?\(\s*(?:true|false)\s*\)"),
    re.compile(r"\b(?:is|has|was|should|can|did)[A-Z]\w*\s*(?::\s*boolean\b|=\s*(?:true|false)\b|\??:\s*bool\b|\s+bool\b)"),
    re.compile(r"self\.(?:is|has|was|should|can|did)_\w+\s*=\s*(?:True|False)\b"),
    re.compile(r"\b(?:is|has|was|should|can|did)_\w+\s*:\s*bool\b"),
]
FLAG_COMBO_RES = [
    re.compile(r"(?:if|while)\s*\(\s*!?\s*(?:is|has|was|should|can|did)[A-Z]\w*\s*(?:&&|\|\|)\s*!?\s*(?:is|has|was|should|can|did)[A-Z]\w*"),
    re.compile(r"\{\s*!?\s*(?:is|has|was|should|can|did)[A-Z]\w*\s*&&\s*!?\s*(?:is|has|was|should|can|did)[A-Z]\w*\s*&&"),
    re.compile(r"if\s+(?:not\s+)?(?:self\.)?(?:is|has|was|should|can|did)_\w+\s+(?:and|or)\s+(?:not\s+)?(?:self\.)?(?:is|has|was|should|can|did)_\w+"),
]


def rule_implicit_state_machine(rel, ext, text, findings):
    hits = []
    for r in FLAG_RES:
        for m in r.finditer(text):
            name = snippet_at(text, m.start())
            if INDEPENDENT_TOGGLE.search(m.group(0)) or re.search(r"(?i)\[\s*(?:is|show|has)\w*(?:open|visible|expanded|collapsed|menu|modal|dialog|drawer|dropdown|tooltip|sidebar|hover|focus|checked|selected|pinned)\w*\s*,", name):
                continue
            hits.append(m.start())
    if len(hits) >= 3:
        first = min(hits)
        findings.append(finding("implicit-state-machine", rel, line_of(text, first),
                                f"{len(hits)} boolean flags in one file; check whether they encode one state", snippet_at(text, first)))
    for r in FLAG_COMBO_RES:
        for m in r.finditer(text):
            findings.append(finding("implicit-state-machine", rel, line_of(text, m.start()),
                                    "condition combines boolean flags; name the state instead", snippet_at(text, m.start())))
    nullable = re.findall(r"useState<[^>]+\|\s*null>\(\s*null\s*\)", text)
    if len(nullable) >= 2 and len(hits) >= 1:
        findings.append(finding("implicit-state-machine", rel, 1,
                                f"{len(nullable)} nullable state slots plus boolean flags; data presence is doing state's job"))


def rule_file_shape(rel, ext, text, findings):
    lines = text.split("\n")
    n = len(lines)
    if n >= 500:
        findings.append(finding("god-files", rel, 1, f"{n} lines in one file"))
    deep = [i for i, l in enumerate(lines) if re.match(r"^(?: {24,}|\t{6,})\S", l)]
    if len(deep) >= 5:
        findings.append(finding("god-files", rel, deep[0] + 1, f"{len(deep)} lines nested six levels or deeper", lines[deep[0]]))
    if ext in PY:
        for m in re.finditer(r"^(\s*)(?:async\s+)?def\s+(\w+)\s*\(", text, re.M):
            indent = len(m.group(1))
            start = line_of(text, m.start())
            end = start
            for j in range(start, n):
                l = lines[j]
                if l.strip() and (len(l) - len(l.lstrip())) <= indent and not l.lstrip().startswith(("#", ")", "]", "}")):
                    break
                end = j + 1
            if end - start > 80:
                findings.append(finding("god-files", rel, start, f"function {m.group(2)} is {end - start} lines", lines[start - 1]))
    elif ext in BRACE:
        for m in re.finditer(r"^\s*(?:export\s+)?(?:(?:public|private|protected|static|async|override|final|pub(?:\([^)]*\))?)\s+)*(?:function\s*\*?\s+(\w+)|func\s+(?:\([^)]*\)\s*)?(\w+)|fn\s+(\w+)|(\w+)\s*\([^)]*\)\s*(?::\s*[^{\n]+)?\s*\{\s*$)", text, re.M):
            name = next((g for g in m.groups() if g), None)
            if not name or name in {"if", "for", "while", "switch", "catch", "else", "return", "match", "defer", "go"}:
                continue
            brace = text.find("{", m.start())
            if brace == -1:
                continue
            depth = 0
            end = None
            for k in range(brace, min(len(text), brace + 20000)):
                c = text[k]
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        end = k
                        break
            if end is None:
                continue
            length = line_of(text, end) - line_of(text, m.start())
            if length > 80:
                findings.append(finding("god-files", rel, line_of(text, m.start()), f"function {name} is {length} lines", snippet_at(text, m.start())))


def rule_try_density(rel, ext, text, findings):
    n = len(re.findall(r"\btry\s*\{|^\s*try\s*:", text, re.M))
    if n >= 8:
        findings.append(finding("defensive-overkill", rel, 1, f"{n} try blocks in one file; most code paths should trust their inputs"))


def rule_options_booleans(rel, ext, text, findings):
    n = len(re.findall(r"\b(?:options|opts|config|settings)\??\.\w+\s*\?\?\s*(?:true|false)\b", text))
    if n >= 4:
        findings.append(finding("over-abstraction", rel, 1, f"{n} boolean option toggles defaulted in one file; check which callers ever set them"))
    barrels = len(re.findall(r"^\s*export\s*\*\s+from\b", text, re.M))
    if barrels >= 5:
        findings.append(finding("over-abstraction", rel, 1, f"barrel file re-exporting {barrels} modules"))


def rule_mixed_async(rel, ext, text, findings):
    if ext in JS:
        awaits = len(re.findall(r"\bawait\b", text))
        thens = len(re.findall(r"\.then\(", text))
        if awaits >= 2 and thens >= 2:
            findings.append(finding("async-misuse", rel, 1, f"mixed styles: {awaits} awaits and {thens} .then chains"))
    if ext in PY and re.search(r"\basync\s+def\b", text):
        for m in re.finditer(r"\btime\.sleep\(|\brequests\.(?:get|post|put|delete|patch)\(", text):
            findings.append(finding("async-misuse", rel, line_of(text, m.start()), "blocking call inside an async module", snippet_at(text, m.start())))


def rule_effect_fetch(rel, ext, text, findings):
    if ext not in JS:
        return
    for m in re.finditer(r"useEffect\(", text):
        block = text[m.start(): m.start() + 1500]
        end = re.search(r"\n\s*\}\s*,\s*\[", block)
        body = block[: end.start()] if end else block
        if re.search(r"\bfetch\(|axios\.|\.get\(|\.post\(|supabase\.|trpc\.|client\.", body) and not re.search(r"AbortController|signal|ignore|cancel|isMounted|mounted|return\s*\(\)\s*=>", body):
            findings.append(finding("react-smells", rel, line_of(text, m.start()), "fetch in an effect with no cancellation; a stale response can win", snippet_at(text, m.start())))


def rule_rust_unwrap(rel, ext, text, findings):
    if ext in RS:
        n = len(re.findall(r"\.unwrap\(\)", text))
        if n >= 5:
            findings.append(finding("type-escape-hatches", rel, 1, f"{n} unwrap calls in one file"))


def rule_commented_code(rel, ext, text, findings):
    if ext in PY:
        code_like = re.compile(r"^\s*#\s*(?:def\s+\w+\(|class\s+\w+|return\b|if\s+.*:\s*$|for\s+.*:\s*$|import\s+\w|from\s+\w+\s+import|\w+\(.*\)\s*$|\w+\s*=\s*\S)")
    else:
        code_like = re.compile(r"^\s*//\s*(?:\}|\{|[\w.]+\(.*\)?;?\s*$|(?:const|let|var)\s+\w+\s*=|return\b.*;|if\s*\(|for\s*\(|while\s*\(|import\s+.*from|export\s+(?:const|function|default|class)|function\s+\w+\s*\(|class\s+\w+)")
    lines = text.split("\n")
    run = 0
    start = 0
    for i, l in enumerate(lines + [""]):
        if code_like.match(l) and "http" not in l:
            if run == 0:
                start = i
            run += 1
        else:
            if run >= 3:
                findings.append(finding("dead-code", rel, start + 1, f"{run} lines of commented-out code", lines[start]))
            run = 0


def rule_tests_without_assertions(rel, ext, text, findings):
    if ext in JS:
        tests = len(re.findall(r"\b(?:it|test)\(\s*['\"`]", text))
        asserts = len(re.findall(r"\bexpect\(|\bassert\.|\bassert\(", text))
        if tests > 0 and asserts < tests:
            findings.append(finding("test-weakening", rel, 1, f"{tests} tests but only {asserts} assertions"))
        mocks = len(re.findall(r"\b(?:jest|vi)\.mock\(", text))
        if mocks >= 5:
            findings.append(finding("test-weakening", rel, 1, f"{mocks} module mocks in one test file; what real code still runs"))
        snaps = len(re.findall(r"toMatchSnapshot\(\)|toMatchInlineSnapshot\(", text))
        if snaps >= 10:
            findings.append(finding("test-weakening", rel, 1, f"{snaps} snapshot assertions in one file"))
        loose = len(re.findall(r"expect\.(?:anything|any)\(", text))
        if loose >= 5:
            findings.append(finding("test-weakening", rel, 1, f"{loose} loose matchers (expect.any / anything)"))
    if ext in PY:
        tests = len(re.findall(r"^\s*(?:async\s+)?def\s+test_\w+", text, re.M))
        asserts = len(re.findall(r"^\s*assert\b|\.assert\w*\(|pytest\.raises\(", text, re.M))
        if tests > 0 and asserts < tests:
            findings.append(finding("test-weakening", rel, 1, f"{tests} tests but only {asserts} assertions"))


STRAY_DOC = re.compile(
    r"(?i)^(?:.*[_-])?(?:SUMMARY|PLAN|NOTES|REPORT|FIXES|ANALYSIS|CHECKLIST|PROGRESS|STATUS|HANDOFF|COMPLETE|"
    r"REFACTOR|IMPLEMENTATION|TESTING|MIGRATION|CHANGES|TODO|VERIFICATION|REVIEW|FINDINGS|CLEANUP|AUDIT|DEBUG|"
    r"INVESTIGATION|NEXT_STEPS|SETUP_GUIDE|QUICKSTART|OVERVIEW|IMPROVEMENTS|RECOMMENDATIONS|COMPARISON|RESULTS)(?:[_-].*)?\.md$"
)
STRAY_KEEP = {"readme.md", "changelog.md", "contributing.md", "license.md", "code_of_conduct.md", "security.md", "claude.md", "agents.md", "gemini.md", "architecture.md", "docs.md", "faq.md", "roadmap.md"}
BACKUP_FILE = re.compile(r"(?i)(?:\.(?:bak|orig|backup|old|tmp|swp|rej)$|[_.-](?:old|backup|bak|copy|fixed|final|original|tmp|new|v2|v3)\.\w+$| 2\.\w+$|\(\d\)\.\w+$|\.copy\.\w+$|_OLD\b|-old\.\w+$)")
SCRATCH_FILE = re.compile(r"(?i)^(?:test|tmp|temp|scratch|debug|check|try|quick|foo|bar|playground|sandbox|experiment)[_-]?\w*\.(?:py|js|ts|sh|mjs|cjs|rb|go|rs)$")
GRABBAG = re.compile(r"(?i)^(?:utils?|helpers?|misc|common|shared|stuff|temp|tmp|functions|lib)\.(?:ts|js|py|go|rs|rb|tsx|jsx|mjs)$")


def rule_stray_files(root, all_rel, findings):
    grabbags = []
    for rel in all_rel:
        base = os.path.basename(rel)
        depth = rel.count("/")
        if BACKUP_FILE.search(base) and not is_test_path(rel):
            findings.append(finding("stray-files", rel, 1, "backup or copy file"))
        if depth == 0 and SCRATCH_FILE.match(base):
            findings.append(finding("stray-files", rel, 1, "scratch script at repo root"))
        if depth <= 1 and not rel.startswith("docs/") and base.lower() not in STRAY_KEEP and STRAY_DOC.match(base):
            findings.append(finding("stray-files", rel, 1, "agent-written summary or plan document"))
        if GRABBAG.match(base) and not is_test_path(rel):
            grabbags.append(rel)
    if len(grabbags) >= 2:
        for g in grabbags:
            findings.append(finding("generic-naming", g, 1, f"grab-bag module ({len(grabbags)} such files); name modules by what they contain"))


def rule_duplicate_helpers(defs, findings):
    for name, locs in defs.items():
        files = sorted({p for p, _ in locs})
        if len(files) >= 2:
            for p, line in sorted(locs):
                others = [f for f in files if f != p]
                findings.append(finding("duplicate-helpers", p, line, f"{name} also defined in {', '.join(others[:3])}"))


def rule_stringly_typed(literals, findings):
    for lit, locs in literals.items():
        files = {p for p, _ in locs}
        if len(files) >= 2 or len(locs) >= 3:
            p, line = sorted(locs)[0]
            findings.append(finding("stringly-typed", p, line, f"'{lit}' compared as a raw string in {len(locs)} places across {len(files)} files; make it a union or enum"))


def nearest_package_json(root, rel_dir, cache):
    cur = rel_dir
    while True:
        key = cur
        if key not in cache:
            pj = os.path.join(root, cur, "package.json") if cur else os.path.join(root, "package.json")
            deps = None
            if os.path.isfile(pj):
                try:
                    data = json.loads(read(pj) or "{}")
                    deps = set()
                    for k in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                        deps |= set((data.get(k) or {}).keys())
                except (json.JSONDecodeError, AttributeError):
                    deps = set()
            cache[key] = deps
        if cache[key] is not None:
            return cache[key]
        if not cur:
            return None
        cur = os.path.dirname(cur)


def collect_workspace_names(root, all_rel):
    names = set()
    for rel in all_rel:
        if os.path.basename(rel) == "package.json":
            try:
                data = json.loads(read(os.path.join(root, rel)) or "{}")
                if isinstance(data, dict) and data.get("name"):
                    names.add(data["name"])
            except json.JSONDecodeError:
                pass
    return names


def py_declared(root, all_rel):
    declared = set()
    found_manifest = False
    for rel in all_rel:
        base = os.path.basename(rel).lower()
        if rel.count("/") > 1:
            continue
        if base.startswith("requirements") and base.endswith(".txt") or base in {"pyproject.toml", "setup.py", "setup.cfg", "pipfile"}:
            found_manifest = True
            txt = read(os.path.join(root, rel)) or ""
            for m in re.finditer(r"(?m)^\s*(?:\"|')?([A-Za-z0-9][A-Za-z0-9._-]*)", txt):
                declared.add(m.group(1).lower().replace("-", "_"))
            for m in re.finditer(r"[\"']([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:[><=!~\[;]|[\"'])", txt):
                declared.add(m.group(1).lower().replace("-", "_"))
    return declared if found_manifest else None


def rule_phantom_js(root, rel, text, pkg_cache, workspace_names, top_dirs, findings):
    deps = nearest_package_json(root, os.path.dirname(rel), pkg_cache)
    if deps is None:
        return
    seen = set()
    for m in JS_IMPORT.finditer(text):
        spec = next((g for g in m.groups() if g), None)
        if not spec or spec.startswith((".", "/", "#", "@/", "~", "$", "node:", "bun:", "deno:", "npm:", "jsr:", "virtual:", "\0")):
            continue
        if spec.endswith((".css", ".scss", ".svg", ".png", ".json")):
            continue
        parts = spec.split("/")
        name = "/".join(parts[:2]) if spec.startswith("@") else parts[0]
        if name in NODE_BUILTINS or name in deps or name in workspace_names or name in top_dirs or name in seen:
            continue
        seen.add(name)
        findings.append(finding("phantom-apis", rel, line_of(text, m.start()), f"'{name}' is imported but not declared in package.json", snippet_at(text, m.start())))


def rule_phantom_py(root, rel, text, declared, local_modules, findings):
    if declared is None:
        return
    seen = set()
    for m in PY_IMPORT.finditer(text):
        mod = (m.group(1) or m.group(2) or "").split(".")[0]
        if not mod or mod in PY_STDLIB or mod in local_modules or mod in seen:
            continue
        norm = mod.lower()
        candidates = {norm, norm.replace("-", "_"), PY_NAME_MAP.get(norm, norm).lower().replace("-", "_")}
        if candidates & declared:
            continue
        if any(d.startswith(norm) for d in declared):
            continue
        seen.add(mod)
        findings.append(finding("phantom-apis", rel, line_of(text, m.start()), f"'{mod}' is imported but not declared in the Python dependency manifest", snippet_at(text, m.start())))


def collect_definitions(ext, rel, text, defs):
    if ext in JS:
        key = "js"
    elif ext in PY:
        key = "py"
    elif ext in GO:
        key = "go"
    elif ext in RS:
        key = "rs"
    else:
        return
    for r in DEF_RES[key]:
        for m in r.finditer(text):
            name = m.group(1)
            if len(name) < 4 or name.lower() in DEF_STOP or name.startswith("_") or name[0].isupper() or name.startswith("use"):
                continue
            defs[name].append((rel, line_of(text, m.start())))


def collect_status_literals(rel, text, literals):
    for m in STATUS_LITERAL.finditer(text):
        lit = m.group(1)
        if lit in STATUS_STOP:
            continue
        literals[lit].append((rel, line_of(text, m.start())))


def scan(root, only=None, exclude=None, include_tests=False, explicit_files=None):
    findings = []
    defs = defaultdict(list)
    literals = defaultdict(list)
    pkg_cache = {}
    all_rel = []
    files_scanned = 0
    for ap in iter_files(root, explicit_files):
        rel = os.path.relpath(ap, root).replace(os.sep, "/")
        all_rel.append(rel)
    top_dirs = {r.split("/")[0] for r in all_rel if "/" in r}
    workspace_names = collect_workspace_names(root, all_rel)
    declared_py = py_declared(root, all_rel)
    local_py = {r.split("/")[0].replace(".py", "") for r in all_rel if r.endswith(".py")} | {r.split("/")[1] if "/" in r else "" for r in all_rel if r.endswith("/__init__.py") or r.endswith(".py")}
    local_py |= top_dirs
    for rel in all_rel:
        ap = os.path.join(root, rel)
        ext = os.path.splitext(rel)[1].lower()
        base = os.path.basename(rel)
        is_doc = ext in DOC_EXT
        is_code = ext in CODE_EXT
        if base == "package.json" or re.match(r"(?:jest|vitest)\.config\.\w+$", base):
            text = read(ap)
            if text:
                run_line_signals(CONFIG_SIGNALS, rel, ext, text, False, False, findings)
            continue
        if not (is_doc or is_code):
            continue
        if GENERATED.search(rel):
            continue
        text = read(ap)
        if text is None or len(text) > 2_000_000 or looks_generated(text):
            continue
        files_scanned += 1
        is_test = is_test_path(rel)
        if is_test:
            run_line_signals(TEST_SIGNALS, rel, ext, text, True, is_doc, findings)
            rule_tests_without_assertions(rel, ext, text, findings)
            if not include_tests:
                continue
        run_line_signals(SIGNALS, rel, ext, text, is_test, is_doc, findings)
        if is_doc:
            continue
        rule_implicit_state_machine(rel, ext, text, findings)
        rule_file_shape(rel, ext, text, findings)
        rule_try_density(rel, ext, text, findings)
        rule_options_booleans(rel, ext, text, findings)
        rule_mixed_async(rel, ext, text, findings)
        rule_effect_fetch(rel, ext, text, findings)
        rule_rust_unwrap(rel, ext, text, findings)
        rule_commented_code(rel, ext, text, findings)
        collect_definitions(ext, rel, text, defs)
        collect_status_literals(rel, text, literals)
        if ext in JS:
            rule_phantom_js(root, rel, text, pkg_cache, workspace_names, top_dirs, findings)
        if ext in PY:
            rule_phantom_py(root, rel, text, declared_py, local_py, findings)
    rule_duplicate_helpers(defs, findings)
    rule_stringly_typed(literals, findings)
    rule_stray_files(root, all_rel, findings)
    findings = [f for f in findings if not CONFIGISH.search("/" + f["path"]) or f["pattern"] not in {"leftover-debug", "hardcoded-config"}]
    if only:
        findings = [f for f in findings if f["pattern"] in only]
    if exclude:
        findings = [f for f in findings if f["pattern"] not in exclude]
    dedup = {}
    for f in findings:
        key = (f["pattern"], f["path"], f["line"], f["note"])
        dedup.setdefault(key, f)
    return list(dedup.values()), files_scanned


def summarize(findings):
    summary = defaultdict(lambda: {"hits": 0, "files": set()})
    for f in findings:
        summary[f["pattern"]]["hits"] += 1
        summary[f["pattern"]]["files"].add(f["path"])
    return summary


def render_markdown(root, findings, files_scanned, max_per_pattern, only=None):
    summary = summarize(findings)
    ordered = sorted(summary.items(), key=lambda kv: (SEVERITY_RANK[PATTERNS[kv[0]][1]], -kv[1]["hits"]))
    out = [f"# slop-audit scan of {root}", "", f"Scanned {files_scanned} files. Test files were checked for test-weakening only.", ""]
    out.append("| pattern | severity | hits | files |")
    out.append("|---|---|---:|---:|")
    for pid, s in ordered:
        out.append(f"| {pid} | {PATTERNS[pid][1]} | {s['hits']} | {len(s['files'])} |")
    if not ordered:
        out.append("| (none) | | 0 | 0 |")
    out.append("")
    for pid, s in ordered:
        title, sev, desc = PATTERNS[pid]
        out.append(f"## {pid} ({sev}, {s['hits']} hits): {title}")
        out.append(f"{desc}.")
        out.append("")
        rows = sorted((f for f in findings if f["pattern"] == pid), key=lambda f: (f["path"], f["line"]))
        for f in rows[:max_per_pattern]:
            out.append(f"- {f['path']}:{f['line']}  {f['note']}")
            if f["snippet"]:
                out.append(f"    `{f['snippet']}`")
        if len(rows) > max_per_pattern:
            out.append(f"- ... {len(rows) - max_per_pattern} more (use --json or --max for all)")
        out.append("")
    semantic = [(k, v) for k, v in SEMANTIC_ONLY.items() if not only or k in only]
    if semantic:
        out.append("## Semantic-only patterns (no grep signal; run their discover prompts)")
        for k, v in semantic:
            out.append(f"- {k}: {v}")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Grep-level first pass for the slop-audit skill. Prints candidates, not verdicts.")
    ap.add_argument("path", nargs="?", default=".", help="repo or directory to scan")
    ap.add_argument("--only", help="comma-separated pattern ids to include")
    ap.add_argument("--exclude", help="comma-separated pattern ids to drop")
    ap.add_argument("--files", nargs="*", help="scan only these files (relative to path); '-' reads paths from stdin")
    ap.add_argument("--include-tests", action="store_true", help="run every pattern on test files too")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--max", type=int, default=25, help="max rows per pattern in markdown output")
    ap.add_argument("--list", action="store_true", help="list pattern ids and exit")
    args = ap.parse_args()

    if args.list:
        for pid, (title, sev, desc) in sorted(PATTERNS.items(), key=lambda kv: (SEVERITY_RANK[kv[1][1]], kv[0])):
            print(f"{pid:24} {sev:7} {title}: {desc}")
        for pid, desc in SEMANTIC_ONLY.items():
            print(f"{pid:24} {'semantic':7} {desc}")
        return

    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        print(f"not a directory: {root}", file=sys.stderr)
        sys.exit(2)
    only = set(args.only.split(",")) if args.only else None
    exclude = set(args.exclude.split(",")) if args.exclude else None
    unknown = (only or set()) | (exclude or set())
    unknown -= set(PATTERNS) | set(SEMANTIC_ONLY)
    if unknown:
        print(f"unknown pattern ids: {', '.join(sorted(unknown))}", file=sys.stderr)
        sys.exit(2)
    explicit = None
    if args.files is not None:
        explicit = [l.strip() for l in sys.stdin if l.strip()] if args.files == ["-"] else args.files
    findings, files_scanned = scan(root, only, exclude, args.include_tests, explicit)
    if args.json:
        summary = {k: {"hits": v["hits"], "files": sorted(v["files"])} for k, v in summarize(findings).items()}
        print(json.dumps({"root": root, "files_scanned": files_scanned, "summary": summary, "findings": findings}, indent=2))
    else:
        print(render_markdown(root, findings, files_scanned, args.max, only))


if __name__ == "__main__":
    main()
