# Rubber Duck Debugger

Rubber Duck Debugger is a small Python command-line sample for exploring
human-in-the-loop tool approval in the OpenAI Agents SDK. It runs a terminal
chatbot that asks about a software bug, drafts a structured bug report, and
saves the report only after human approval.

> [!WARNING]
> This is an experimental project and should not be considered production-ready.

The project is intentionally small so the approval workflow stays visible. The
agent gathers enough information to write a bug report, calls a file-writing
tool that requires approval, and lets the human either approve the report or ask
for revisions before the tool runs.

## What It Does

The CLI starts an interactive chat session:

```powershell
.\.venv\Scripts\python.exe -m rubber_duck_debugger
```

The agent then:

- asks focused follow-up questions about a software bug
- creates a Markdown bug report with summary, context, reproduction steps,
  expected behavior, actual behavior, and severity
- requests approval before saving the report
- revises the report when approval is rejected
- saves the approved report to `bugs/bug-001.md`
- ends the chat after the report is created, or when the user says a report is
  no longer needed

## Requirements

- Python 3.11.
- PowerShell on Windows.
- An `OPENAI_API_KEY` environment variable for OpenAI model calls.

## Setup

Create the virtual environment and install the project with development
dependencies:

```powershell
.\scripts\setup-dev.ps1
```

The setup script expects Python 3.11 at the path configured in
`scripts\setup-dev.ps1`.

## Running

Run the chatbot from the repository root:

```powershell
.\.venv\Scripts\python.exe -m rubber_duck_debugger
```

Describe a bug in the terminal. When the agent has enough information, it will
show the proposed report and ask whether the `create_bug_report` tool should be
approved.

## Development Checks

Run formatting, linting, type checking, and tests:

```powershell
.\scripts\check.ps1
```

This runs:

- `ruff format .`
- `ruff check .`
- `pyright`
- `pytest`

## Project Structure

```text
src/rubber_duck_debugger/
  __main__.py   Package entry point for python -m rubber_duck_debugger
  cli.py        Agent setup, chat loop, and approval handling
  tools.py      Agent tools for saving reports and ending chats

tests/
  test_smoke.py

scripts/
  setup-dev.ps1
  check.ps1
```

## Notes

This project is a human-in-the-loop learning exercise, not a real issue tracker
integration. The saved bug report is written to a local Markdown file so the
approval behavior can be tested without external systems.

Agent behavior and final wording can vary between runs because the conversation
and tool selection are model-driven. OpenAI API calls may incur usage costs.

## Third-Party Notices

This project has a direct runtime dependency on the `openai-agents` Python
package (MIT). See the package's PyPI license metadata for full license and
notice terms.

## License

GNU General Public License v3.0. See the `LICENSE` file for details.
