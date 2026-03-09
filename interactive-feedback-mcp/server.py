# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by Pau Oliva (https://x.com/pof) with ideas from https://github.com/ttommyth/interactive-mcp
# Modified: Use MCP Elicitation for inline display in Cursor chat
import os
import sys
import json
import asyncio
import tempfile
import subprocess

from typing import Dict, Literal

from fastmcp import FastMCP, Context
from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation
from pydantic import Field, create_model

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

# Prevent concurrent elicitation requests from different conversations
# within the same Cursor window (they share one MCP server process via stdio).
# Without this, two simultaneous ctx.elicit() calls cause cross-contamination.
_feedback_lock = asyncio.Lock()


def _build_feedback_model(options: list[str]):
    """Dynamically build a Pydantic model with enum options + free text input.
    Creates a form with radio buttons for predefined options AND a text input box.
    """
    OptionsLiteral = Literal[tuple(options)]
    return create_model(
        'FeedbackForm',
        answer=(OptionsLiteral, Field(description="Select an option")),
        other=(str, Field(default="", description="Or type your own response here")),
    )


def launch_feedback_ui(summary: str, predefinedOptions: list[str] | None = None) -> dict[str, str]:
    """Fallback: launch Qt feedback UI as a separate process."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        feedback_ui_path = os.path.join(script_dir, "feedback_ui.py")

        args = [
            sys.executable, "-u", feedback_ui_path,
            "--prompt", summary,
            "--output-file", output_file,
            "--predefined-options", "|||".join(predefinedOptions) if predefinedOptions else ""
        ]
        result = subprocess.run(
            args, check=False, shell=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL, close_fds=True
        )
        if result.returncode != 0:
            raise Exception(f"Failed to launch feedback UI: {result.returncode}")

        with open(output_file, 'r') as f:
            result = json.load(f)
        os.unlink(output_file)
        return result
    except Exception as e:
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e


@mcp.tool()
async def interactive_feedback(
    message: str = Field(description="The specific question for the user"),
    predefined_options: list = Field(default=None, description="Predefined options for the user to choose from (optional)"),
    ctx: Context = None,
) -> Dict[str, str]:
    """Request interactive feedback from the user"""

    # Reject concurrent requests: asyncio is single-threaded so locked() + acquire
    # is atomic (no yield point between check and the sync path of acquire).
    if _feedback_lock.locked():
        return {
            "interactive_feedback": "",
            "status": "busy",
            "error": "Another feedback dialog is already active in this window. "
                     "Please answer that one first, then retry.",
        }

    async with _feedback_lock:
        predefined_options_list = predefined_options if isinstance(predefined_options, list) else None

        response_type = None
        if predefined_options_list and len(predefined_options_list) > 0:
            options = [str(opt) for opt in predefined_options_list]
            response_type = _build_feedback_model(options)

        try:
            result = await ctx.elicit(
                message=message,
                response_type=response_type,
            )

            if isinstance(result, AcceptedElicitation):
                feedback = result.data
                if isinstance(feedback, dict):
                    parts = [str(v) for v in feedback.values() if v]
                    return {"interactive_feedback": "\n".join(parts) if parts else ""}
                elif isinstance(feedback, list):
                    return {"interactive_feedback": "; ".join(str(f) for f in feedback)}
                else:
                    return {"interactive_feedback": str(feedback) if feedback else ""}
            elif isinstance(result, DeclinedElicitation):
                return {"interactive_feedback": "", "status": "declined"}
            elif isinstance(result, CancelledElicitation):
                return {"interactive_feedback": "", "status": "cancelled"}
            else:
                return {"interactive_feedback": str(result)}

        except Exception:
            # Fallback to Qt UI if elicitation is not supported
            return launch_feedback_ui(message, predefined_options_list)


if __name__ == "__main__":
    mcp.run(transport="stdio")
