import time
import anthropic
from typing import Any, Callable
from app.tracer import Tracer
from app.config import ANTHROPIC_API_KEY, MODEL, OPENROUTER_BASE_URL, OPENROUTER_HEADERS

_client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    default_headers=OPENROUTER_HEADERS,
)


def run_agent(
    agent_name: str,
    system_prompt: str,
    user_message: str,
    tools: list[dict],
    tool_dispatch: Callable[[str, dict], Any],
    tracer: Tracer,
    max_iterations: int = 10,
    max_tokens: int = 2000,
) -> tuple[str, int]:
    """
    Run a Claude agent with tool use until it produces a final text response.
    Returns (final_text, total_tokens_used).
    """
    messages = [{"role": "user", "content": user_message}]
    total_tokens = 0

    for _ in range(max_iterations):
        response = _client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )
        total_tokens += response.usage.input_tokens + response.usage.output_tokens

        if response.stop_reason == "end_turn":
            text_blocks = [b for b in response.content if b.type == "text"]
            return (text_blocks[0].text if text_blocks else ""), total_tokens

        if response.stop_reason == "tool_use":
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tu in tool_uses:
                start = time.time()
                result = tool_dispatch(tu.name, tu.input)
                duration_ms = int((time.time() - start) * 1000)
                tracer.record(agent_name, tu.name, tu.input, result, duration_ms)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": str(result),
                })
            messages.append({"role": "user", "content": tool_results})

    return "Max iterations reached without final answer", total_tokens
