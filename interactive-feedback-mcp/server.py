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
import logging
import tempfile
import subprocess

from typing import Dict, Literal

from fastmcp import FastMCP, Context
from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation
from pydantic import Field, create_model

mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feedback-debug.log")
logger = logging.getLogger("interactive_feedback")
logger.setLevel(logging.DEBUG)
_fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(_fh)

HEARTBEAT_INTERVAL = 30


async def _elicit_with_heartbeat(ctx: Context, message: str, response_type, timeout: float = 1800.0):
    """Run ctx.elicit() while sending periodic heartbeats to prevent MCP/Cursor transport timeout."""
    elicit_task = asyncio.create_task(
        ctx.elicit(message=message, response_type=response_type)
    )

    elapsed = 0.0
    while not elicit_task.done():
        try:
            await ctx.report_progress(progress=0, total=1, message="waiting")
        except Exception:
            pass
        try:
            await asyncio.wait_for(asyncio.shield(elicit_task), timeout=HEARTBEAT_INTERVAL)
        except asyncio.TimeoutError:
            elapsed += HEARTBEAT_INTERVAL
            if elapsed >= timeout:
                elicit_task.cancel()
                raise asyncio.TimeoutError()
            continue

    return elicit_task.result()


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
    logger.info("interactive_feedback called: message=%r, options=%r", message, predefined_options_list)

    response_type = None
    if predefined_options_list and len(predefined_options_list) > 0:
        options = [str(opt) for opt in predefined_options_list]
        response_type = _build_feedback_model(options)

    try:
        result = await _elicit_with_heartbeat(ctx, message, response_type)
        logger.info("elicit result type=%s, value=%r", type(result).__name__, result)

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
            logger.warning("User declined elicitation")
            return {"interactive_feedback": "", "status": "declined"}
        elif isinstance(result, CancelledElicitation):
            logger.warning("Elicitation cancelled (dialog dismissed)")
            return {"interactive_feedback": "", "status": "cancelled"}
        else:
            logger.warning("Unexpected result type: %s", type(result).__name__)
            return {"interactive_feedback": str(result)}

    except asyncio.TimeoutError:
        logger.error("Elicitation timed out (1800s)")
        return {"interactive_feedback": "", "status": "timeout",
                "error": "Feedback dialog timed out (1800s)."}
    except Exception as e:
        logger.error("Elicitation exception: %s, falling back to Qt UI", e, exc_info=True)
        return _launch_feedback_ui(message, predefined_options_list)


if __name__ == "__main__":
    mcp.run(transport="stdio")
