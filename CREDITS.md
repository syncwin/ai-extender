# Credits

AI Extender is an independent implementation. It doesn't fork, copy, or need any third-party skill, plugin, or code at runtime. Every capability was written for this plugin from the official Claude documentation (code.claude.com/docs and claude.com/docs) after studying how other tools approach the same jobs.

Studied, then rewritten:

- Anthropic's `/skill-creator`: the test, baseline, grading, and description-tuning loop informed `claude-developer/references/testing.md` and `scripts/aggregate_results.py`; its packaging and validation steps informed the packager and reviewer scripts.
- Anthropic's `/create-cowork-plugin` and `/cowork-plugin-customizer`: the Cowork build and customization flow in `claude-packager/references/cowork.md` and `claude-maintainer/references/updating.md`.
- Anthropic's `plugin-dev` and `mcp-server-dev` plugins: their scope only (what plugin, hook, and MCP authoring should cover).
- [Ponytail](https://github.com/DietrichGebert/ponytail), an open-source Claude skill: the lean-implementation principle.

Training data for the injection screen (`claude-reviewer/scripts/injection_model.json`, weights learned here; no data or model files are redistributed):

- [deepset/prompt-injections](https://huggingface.co/datasets/deepset/prompt-injections), Apache-2.0.
- [jackhhao/jailbreak-classification](https://huggingface.co/datasets/jackhhao/jailbreak-classification), Apache-2.0.
- Benchmarks consulted, not used as training data: Red Hat's "Benchmarking AI decision models against traditional guardrails" (2026-10-02), covering `protectai/deberta-v3-base-prompt-injection-v2` and Laya.

Not affiliated with or endorsed by Anthropic.
