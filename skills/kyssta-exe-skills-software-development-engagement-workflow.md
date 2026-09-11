---
name: engagement-workflow
category: software-development
description: >-
  Guidelines for engaging with the user when making changes, based on lessons learned from user frustration.
trigger: >-
  making changes to the codebase, updating skills, or any task that involves modifying files based on user requests.
---

# Engagement Workflow

When the user asks about a gap, missing feature, or evaluation:

 1. **Deliver verdict first.** Read the code, trace the flow, then answer their question with your analysis. Do NOT touch any files until the user explicitly says "do it" / "yes" / "make changes."
 2. **Wait for green-light.** The user decides when coding starts. If you start editing before they say yes, you'll waste time on changes they might not want.
 3. **Batch ALL changes.** When you do edit, search for ALL files that need the same change. The user will call you out if you update README.md but miss docs/index.md and docs/install.md. Use `search_files` before the first edit to find every occurrence.
 4. **Test after batch, not after every edit.** One test run per batch. Run the full e2e test. Fix all compile errors in one pass, not incrementally.
 5. **Ponytail applies to code, not to understanding.** Read everything before climbing the ladder. The user's frustration comes from incomplete execution, not from lazy code.

 ## Known pitfalls from recent session

 - **Escaping in skill patches**: When using skill_manage with action='patch', ensure that the old_string and new_string are exactly as they appear in the file, without extra escaping. Avoid using strings that contain backslashes or quotes if possible, or use a longer unique context.
 - **Dialoguer type annotation**: `Input::with_theme(&theme)` returns `Input<T>` where `T` defaults to `()`. Always annotate: `let model: String = Input::with_theme(&theme)...interact()?;`
 - **Edition 2015 false positive**: The Rust 2021 linter sometimes emits false positives about edition 2015 async. Ignore them — `cargo build` succeeds despite the lint output.
 - **Binary name vs crate name**: Changing `[package] name` in Cargo.toml changes the binary name AND the crate name. This affects `cargo build -p <name>`. The directory path stays the same for workspace members.
 - **Webhook `run_id` clone**: When spawning `execute_workflow` in a tokio::spawn, the `run_id` is moved into the closure. Clone it before the spawn to use in the response.
 - **SQLite multi-statement**: `sqlx::query(include_str!(\"...\")).execute()` runs only the FIRST statement. Use multiple calls or `sqlx:raw_sql` for batches.
 - **Observer schema consistency**: The observability.rs module queries the database schema directly. When modifying database tables (especially steps table), you must update the SQL queries and row structs in observability.rs to match the actual schema.
 - **Tool listing completeness**: The `tools` command only lists tools from the `_HERMES_CORE_TOOLS` constant in toolsets.py. When adding new built-in tools, they must be added to this constant to appear in the tools listing.
 - **LLM context budgeting**: The `trim_context_tokens` function in executor.rs should use a conservative limit (1500-2000 characters) to leave room for the prompt and completion. Starting with 4000+ can cause context overflow errors with some models.
 - **Engagement workflow violation**: Starting to make changes before getting explicit user confirmation after analysis. Follow the engagement workflow: deliver verdict first, wait for green-light, batch all changes, test after batch.