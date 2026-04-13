# 🤖 System Harness: Life Canvas OS Development 
You are the AI co-pilot for "Life Canvas OS". This document is your foundational Harness. You MUST strictly adhere to the guardrails defined below. Do not bypass these constraints.

## 🧱 1. Architectural Guardrails (System Boundaries)
Your code generation must respect these immutable technical boundaries:

* **State Management Strictness:**
    * Server State: **MUST** use `TanStack Query`. NEVER use `useState` or `useEffect` for fetching API data.
    * Global State: **MUST** use `React Context` (`AppContext`). NEVER introduce `Zustand` or `Redux`.
    * Form State: **MUST** use `react-hook-form` + `zod`.
* **Dual-Mode Backend Awareness:** * Frontend IPC calls (`window.App.request`) map dynamically. When writing frontend API calls, assume IPC length-prefixed JSON protocol for production, but DO NOT hardcode IPC logic into React components. Use the established preload bridge.
* **Response Formatting:** All FastAPI endpoints MUST return data wrapped in `success_response()` or `error_response()` from `backend/schemas/common.py`. Raw dicts are forbidden.

## 🧠 2. Context & Memory Guardrails (How to Think)
Do not hallucinate project structures or business logic. Rely on deterministic context:

* **The 8-Dimension Model:** All features revolve around the 8 dimensions (FUEL, PHYSICAL, INTELLECTUAL, OUTPUT, DREAM, ASSET, CONNECTION, ENVIRONMENT). When proposing new features, explicitly map them to this model.
* **No Guessing Imports:** Before importing a shared component or Python utility, use your search tools to verify its exact path. Use `~/` for all frontend imports (resolves to `src/`). NEVER use relative paths like `../../`.
* **Pydantic V2 Strictness:** We use Pydantic V2. Use `model_config = ConfigDict(...)` instead of `class Config`. Avoid protected namespaces (e.g., `model_name`).

## ⚙️ 3. Verification & Self-Correction Guardrails (How to Act)
Treat every code generation as an experiment that might fail. Build your own safety nets:

* **Pydantic / Type Verification:** If you modify a FastAPI schema or React interface, you MUST immediately check if existing services/components break.
* **ReAct Loop Emulation:** When implementing the AI Agent module (`backend/agent/`), ensure you write comprehensive Error Logs to be passed back to the LLM observation step. DO NOT swallow errors in the Agent execution layer.
* **Formatting Compliance:** Output clean code. Indent with 2 spaces. Line width max 80 chars. You do not need to run Biome yourself, but your code must closely match Biome standards (no explicit any is allowed, but prefer strict types). Max 50 lines for logic, 100 lines for components.

## 🛡️ 4. Tool & Permission Guardrails (What NOT to do)
* **Immutable Data:** NEVER generate scripts or commands that directly modify or delete the SQLite database in `--data-dir` without explicit human confirmation.
* **High-Risk Operations:** If tasked with writing UI for deleting Diaries or modifying user settings, you MUST automatically include a secondary confirmation modal or logic.
* **Component Modularity:** Do not write monolithic files. If you generate a file exceeding 300 lines, stop and refactor it into smaller sub-components immediately.

## 📌 Context Injection (Read Before Coding)
* Frontend: `Electron` + `React 19` + `Vite` + `shadcn/ui` + `TailwindCSS`
* Backend: `Python 3.12` + `FastAPI` + `SQLAlchemy` + `SQLite` (IPC/HTTP dual mode)
* Start Dev: `pnpm dev`
* Lint: `pnpm lint:fix`

*Acknowledge these harness constraints silently and apply them to all subsequent outputs.*

## 🌏 5. Localization & Chinese Developer Guardrails
You are assisting a Chinese developer. Your generated code, text, and terminal commands must respect the following localization rules:

* **Strict Naming vs. Comments (命名与注释严格分离):** * **Code/Variables/Files:** MUST use standard English (e.g., `user_profile`, `fetchData`). **NEVER use Pinyin** (e.g., `yonghu_ziliao` is strictly forbidden).
  * **Comments/Docs/Git Commits:** MUST be written in clear, professional Chinese. Explain complex logic in Chinese comments.
  * **UI Text:** All user-facing text in React components must be in Chinese unless specified otherwise.
* **Timezone Awareness (时区感知):**
  * The project operates in the **UTC+8** timezone (Singapore/Beijing time). 
  * When generating Python datetime logic or React date formatting (e.g., using `dateUtils.ts` or `date-fns`), always account for UTC+8. Prefer `YYYY-MM-DD HH:mm:ss` format for logs and UI.
* **Typography Formatting (中英文排版规范):**
  * When writing Chinese documentation, comments, or UI text, you MUST insert a single space between Chinese characters and English words/numbers (e.g., `这是一个 API 接口` instead of `这是一个API接口`).
* **Environment & Scripts (网络与依赖环境):**
  * If generating terminal commands to install dependencies, assume standard environments, but if specifically asked to optimize for Chinese networks, append reliable mirrors (e.g., `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple` or `npm --registry=https://registry.npmmirror.com`).
