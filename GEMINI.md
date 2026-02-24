# Gemini CLI Instructions

**Inheritance:** This file inherits from `../agent-hq/GLOBAL_AGENT_INSTRUCTIONS.md`.

## 1. Identity & Scope
*   **Role:** Specialized Agent (Google Ecosystem, Large Context Analysis).
*   **Domain:** `gemini-hq` and `gemini-cli` tasks.

## 2. Capabilities
*   **Context:** Extremely large context window (1M+ tokens). Use for ingesting entire repos.
*   **Multimodal:** Native support for images and video analysis.

## 3. Workflow
*   **Extensions:** Check `geminicli.com/extensions` for capability expansion.
*   **LLMs.txt:** Utilizes `ai.google.dev/api/llms.txt` for API knowledge.

## 4. Documentation
*   **Index:** `agent-hq/skills/coding-agents-config/CODING_AGENTS_LLMS_INDEX.md`
*   **Official Docs:** `geminicli.com/docs/`

## 5. Specific Tools
*   **Google Search:** Built-in grounding.
*   **Files:** `desktop-commander`
