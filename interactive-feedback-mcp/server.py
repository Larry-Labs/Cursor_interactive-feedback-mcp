# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Enhanced by Pau Oliva (https://x.com/pof)
# Concurrent-safe: each tool call runs independently with its own Context,
# no global state or preemptive cancellation — multiple conversations can
# call interactive_feedback simultaneously without interfering.
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

mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")


def _build_feedback_model(options: list[str]):
    """Dynamically build a Pydantic model with enum options + free text input."""
    OptionsLiteral = Literal[tuple(options)]
    return create_model(
        'FeedbackForm',
        answer=(OptionsLiteral, Field(description="Select an option")),
        other=(str, Field(default="", description="Or type your own response here")),
    )


def _launch_feedback_ui(summary: str, predefined_options: list[str] | None = None) -> dict[str, str]:
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
            "--predefined-options", "|||".join(predefined_options) if predefined_options else ""
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
    """Request interactive feedback from the user.

    Each call is fully independent — no shared global state. Multiple
    conversations can invoke this tool concurrently without interference.
    """
    predefined_options_list = predefined_options if isinstance(predefined_options, list) else None

    response_type = None
    if predefined_options_list and len(predefined_options_list) > 0:
        options = [str(opt) for opt in predefined_options_list]
        response_type = _build_feedback_model(options)

    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            result = await asyncio.wait_for(
                ctx.elicit(message=message, response_type=response_type),
                timeout=1800.0,
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

        except asyncio.TimeoutError:
            return {"interactive_feedback": "", "status": "timeout",
                    "error": "Feedback dialog timed out (1800s)."}
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue

    try:
        return _launch_feedback_ui(message, predefined_options_list)
    except Exception:
        raise Exception(
            f"Elicitation failed after {max_retries} retries "
            f"(last error: {last_error}), and Qt fallback is unavailable."
        )


if __name__ == "__main__":
    mcp.run(transport="stdio")
