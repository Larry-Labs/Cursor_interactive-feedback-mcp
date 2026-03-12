# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by Pau Oliva (https://x.com/pof) with ideas from https://github.com/ttommyth/interactive-mcp
# Modified: Use MCP Elicitation for inline display in Cursor chat
from typing import Dict, Literal

from fastmcp import FastMCP, Context
from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation
from pydantic import Field, create_model

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

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


@mcp.tool()
async def interactive_feedback(
    message: str = Field(description="The specific question for the user"),
    predefined_options: list | None = Field(default=None, description="Predefined options for the user to choose from (optional)"),
    ctx: Context = None,
) -> Dict[str, str]:
    """Request interactive feedback from the user"""

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

    except Exception as e:
        return {
            "interactive_feedback": "",
            "status": "error",
            "error": f"Elicitation failed: {e}. Please ask the user directly in chat.",
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
