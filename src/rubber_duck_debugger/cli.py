"""Command-line interface for the application."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

from agents import Agent, Runner, RunResult
from agents.items import ItemHelpers, MessageOutputItem

from rubber_duck_debugger.tools import create_bug_report, end_chat

SHOW_DEBUGGING = False


@dataclass
class ApprovalResult:
    result: RunResult
    should_end_chat: bool


async def main(argv: list[str] | None = None) -> None:
    """Run the command-line interface."""
    parser = _build_parser()
    parser.parse_args(argv)
    print("Tell me about the software bug. Type 'quit' to exit.")

    instructions = """
You are Rubber Duck Debugger, a CLI chatbot that helps create bug reports.

Your job is to gather enough information to create a Markdown bug report with
these sections:

```
# Bug Report

## Summary
{A short summary of the bug.}

## Context
{In what context does the bug occur?}

## Steps to reproduce
{Simple steps which cause the bug to occur.}

## Expected behavior
{What is the correct behavior, if the bug did not exist?}

## Actual behavior
{What is the behavior which occurs, caused by the bug?}
```

If you do not yet have enough information, ask exactly one focused follow-up
question.

When you have enough information, do not ask the user whether to save the report.
Instead, call the create_bug_report tool with the complete Markdown bug report.

If the user says they no longer need a bug report, have figured out the bug,
or want to stop, call the end_chat tool with a short reason.
"""

    conversation = []

    agent = Agent(
        name="Rubber Duck Debugger",
        instructions=instructions,
        tools=[create_bug_report, end_chat],
    )

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Done.")
            return

        if conversation:
            conversation.append({"role": "user", "content": user_input})
            result = await Runner.run(agent, conversation)
        else:
            result = await Runner.run(agent, user_input)

        if SHOW_DEBUGGING:
            print("DEBUG final_output:", repr(result.final_output))
            print("DEBUG interruptions:", len(result.interruptions))
            print("DEBUG new_items:")
            for item in result.new_items:
                print("  ", type(item).__name__, getattr(item, "type", None))
            for item in result.new_items:
                print("  ", type(item).__name__, getattr(item, "type", None))

                if isinstance(item, MessageOutputItem):
                    text = ItemHelpers.text_message_output(item)
                    print("     text:", repr(text))

        approval_result = await _handle_tool_approvals(agent, result)
        result = approval_result.result

        duck_message = _get_duck_message(result)
        if duck_message:
            print("Duck:", duck_message)

        if approval_result.should_end_chat or _did_call_end_chat(result):
            return

        conversation = result.to_input_list()


async def _handle_tool_approvals(agent: Agent, result: RunResult) -> ApprovalResult:
    while result.interruptions:
        interruption = result.interruptions[0]

        print("Duck wants to create a bug report.")

        arguments = interruption.arguments
        if arguments is not None:
            tool_args = json.loads(arguments)
            proposed_report = tool_args["report"]

            print("------")
            print(proposed_report)
            print("------")

        approval = input("Create this bug report? (y/n): ")

        state = result.to_state()

        if approval.lower() == "y":
            state.approve(interruption)
            result = await Runner.run(agent, state)
            return ApprovalResult(result=result, should_end_chat=True)
        else:
            changes = input("Duck: What should be changed in the bug report?\nYou: ")

            state.reject(
                interruption,
                rejection_message=(
                    "The human rejected the proposed bug report. "
                    "Revise the bug report according to this request, "
                    "then call create_bug_report again with the updated report. "
                    f"Requested change: {changes}"
                ),
            )

        result = await Runner.run(agent, state)

    return ApprovalResult(result=result, should_end_chat=False)


def _get_duck_message(result: RunResult) -> str:
    if result.final_output:
        return str(result.final_output)

    messages = []

    for item in result.new_items:
        if isinstance(item, MessageOutputItem):
            text = ItemHelpers.text_message_output(item)
            if text:
                messages.append(text)

    if messages:
        return messages[-1]

    return ""


def _did_call_end_chat(result: RunResult) -> bool:
    for item in result.new_items:
        if getattr(item, "type", None) == "tool_call_item":
            raw_item = getattr(item, "raw_item", None)
            name = getattr(raw_item, "name", None)
            if name == "end_chat":
                return True

    return False


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Rubber Duck Debugger.",
    )
    return parser
