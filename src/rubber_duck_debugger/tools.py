from __future__ import annotations

from pathlib import Path

from agents import function_tool


@function_tool(needs_approval=True)
def create_bug_report(report: str) -> str:
    """Create the bug report in the issue tracking system."""
    root_directory = Path.cwd()
    bugs_directory = root_directory / "bugs"
    if not bugs_directory.exists():
        bugs_directory.mkdir(parents=True, exist_ok=True)
    bug_filename = "bug-001.md"
    bug_file = bugs_directory / bug_filename
    with open(bug_file, "w", encoding="utf-8") as file:
        file.write(report)
    return f"Saved {bug_filename}"


@function_tool
def end_chat(reason: str) -> str:
    """End the chat because the user no longer needs a bug report."""
    return reason
