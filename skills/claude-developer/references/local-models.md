# Local Decision Models and Docker

Load when a user asks for a small local model (classifier, decision model, guardrail) or for Docker in an extension. Findings checked 2026-10-11; the benchmark is Red Hat's "Benchmarking AI decision models against traditional guardrails" (developers.redhat.com, 2026-10-02).

## Contents

1. What the benchmark found · 2. Where a local model fits · 3. Where it doesn't · 4. How to add one · 5. Docker

## 1. What the benchmark found

| Model | Kind | Size | Prompt injection | Content safety | Median latency | Runs on |
|---|---|---|---|---|---|---|
| `deberta-v3-base-prompt-injection-v2` | trained classifier | ~200M | 89.0% | n/a | 54 ms | laptop CPU |
| `granite-guardian-hap-125m` | trained classifier | 125M | n/a | 80.3% | 33 ms | laptop CPU |
| Laya (ModernBERT) | zero-shot decision model | 421M | 85.4% | 57.9% (75.2% tuned) | 119 ms | laptop CPU |
| DiffusionGemma | zero-shot decision model | 2.6B | 87.7% | 85.5% | 562 ms | GPU |
| Jev (hosted API) | zero-shot decision model | unknown | 86.4% | 86.2% | 348 ms | remote |
| Qwen3.6-35B as judge | LLM judge | 35B | 89.3% | 85.5% | 312 ms | GPU |

The authors' conclusion: where labeled data exists, a small trained classifier matches large judges at a fraction of the cost. Zero-shot decision models are a usable fallback when no trained classifier exists, but they were not faster or more accurate than an LLM judge. Prompts tuned for one decision model can hurt another (Laya gained 17.8 points from a tuned policy; Jev lost 3.7 on the same policy).

## 2. Where a local model fits

One job: screening untrusted text before Claude acts on it. A Claude Code `PostToolUse` hook on `WebFetch` and connector tools can run a prompt-injection classifier over the returned content and warn (or block with exit 2) when it scores high. This backs up standards §5c (tool output is data, never instructions) with a check that costs no tokens.

## 3. Where it doesn't

- **Routing and skill choice.** Measured 2026-10-12 on AI Extender itself: 60 requests labeled with the right skill and reference file, routed by pure-Python stand-ins for the two model types. A zero-shot ranker over 199 skill and reference sections (Laya-style) picked the right skill 58% of the time and the right file 35% (60% within its top 3). A classifier trained on the other 59 labels plus the 45 trigger phrases in the skill descriptions (DeBERTa-style, leave-one-out) reached 42%, and combining the two 52%. Claude picks the skill from the same descriptions at no extra cost and fired the right one in nearly every live eval run. A local model would add a tool call or a hook (Claude Code and Cowork only) to be wrong more often. Revisit only if a plugin collects a few hundred real routing decisions to train on. What already works at zero runtime cost: trigger phrases in descriptions, a router table that names every skill (`S019`), and `claude-reviewer/scripts/simulate.py` to test them.
- **Chat on claude.ai, and the Skills API.** Chat runs skills and commands only, and the API container has no network or package installs, so no local model can run there. Hooks and local servers run in Cowork and Claude Code.
- **As the only gate.** False positives block real work and false negatives pass. Always pair it with the rules check and Claude's own reading.

## 4. How to add one (Claude Code add-on, opt-in)

- Ship it as a **separate add-on plugin** (`addons.md`), never inside a plugin bound for the directory: the model download and the PyTorch or ONNX runtime are large, need the network on first run, and get held for review.
- Install into `${CLAUDE_PLUGIN_DATA}` from a `SessionStart` hook, as `scaffold_mcp_server.py --lang python` does. Pin package versions and the model revision. An ONNX export runs without PyTorch and starts faster.
- Disclose the download, its size, and what text it reads in the README section "What it runs, reads, and sends".
- Fail open with a visible note when the model is missing or slow (set a timeout), and measure false positives with evals before turning blocking on.

## 5. Docker

- **Docker Agent** (`docker agent`, formerly cagent) defines agents in YAML and runs them in Docker's own runtime. It is another agent platform, not a Claude extension type. It fits as a future platform layer beside the Claude one (`ai-extender/references/platforms.md`), not inside today's plugins.
- **Docker MCP Gateway** runs MCP servers in containers. A Claude Code plugin can declare it as a local connector (`"command": "docker"`, image pinned by digest) to isolate a server it doesn't trust. Chat and Cowork connectors run from Anthropic's cloud and need a public URL, so this is Claude Code only.
- **Docker Model Runner** serves local models behind an OpenAI-style endpoint. It suits small generative models. Encoder classifiers such as DeBERTa run more simply through ONNX or transformers (§4).
- Every Docker route needs Docker Desktop on the user's machine. Say so in the plan, and keep a path that works without it.
