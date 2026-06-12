import os
import re
import subprocess
import sys
from collections.abc import Iterator

import requests

# Strip generic Hermes display/action tags.
_ACTION_TAG_RE = re.compile(r"<action\s+[^>]*/>")

# Map known action tags to visible "thinking" steps.
_ACTION_THINK_MAP = {
    "thinking": "🤔 正在思考...",
    "confused": "❓ 有点疑惑...",
    "talking": "💬 准备回答...",
    "shy": "😳 有点害羞...",
    "sleepy": "😴 有点困了...",
}

_EMOTION_MAP = {
    "joy": "开心",
    "sadness": "难过",
    "anger": "生气",
    "surprise": "惊讶",
    "fear": "害怕",
    "disgust": "厌恶",
    "embarrassed": "害羞/激动",
    "neutral": "平静",
}

# Hermes Agent exposes an OpenAI-compatible API server on localhost by default.
_API_SERVER_HOST = os.environ.get("API_SERVER_HOST", "127.0.0.1")
_API_SERVER_PORT = int(os.environ.get("API_SERVER_PORT", "8642"))
_API_SERVER_URL = f"http://{_API_SERVER_HOST}:{_API_SERVER_PORT}/v1/chat/completions"
_API_SERVER_KEY = os.environ.get("API_SERVER_KEY")
_API_SERVER_MODEL = os.environ.get("HERMES_API_MODEL", "hermes-agent")

# Fallback provider/model if the default Hermes config fails.
_FALLBACK_PROVIDER = os.environ.get("HERMES_FALLBACK_PROVIDER", "minimax-cn")
_FALLBACK_MODEL = os.environ.get("HERMES_FALLBACK_MODEL", "abab6-chat")


def _strip_action_tags(text: str) -> str:
    return _ACTION_TAG_RE.sub("", text)


def _transform_actions_to_thinking(text: str) -> str:
    """Convert Hermes action tags into visible <think> steps, then strip leftovers."""
    if not text:
        return text

    out = text
    # name="..."
    for name, label in _ACTION_THINK_MAP.items():
        out = re.sub(
            rf"<action\s+name=\"{re.escape(name)}\"\s*/>",
            f"<think>{label}</think>",
            out,
        )

    # emotion="..."
    for emotion, label in _EMOTION_MAP.items():
        out = re.sub(
            rf"<action\s+emotion=\"{re.escape(emotion)}\"\s*/>",
            f"<think>情绪：{label}</think>",
            out,
        )

    # Remove any remaining unknown action tags.
    return _ACTION_TAG_RE.sub("", out)


class Pipe:
    def pipe(self, body: dict, __user__: dict = None):
        messages = body.get("messages", [])
        if not messages:
            return "No messages provided."

        last_msg = messages[-1]
        if last_msg.get("role") != "user":
            return "Waiting for user message..."

        user_prompt = last_msg.get("content", "")
        if not user_prompt:
            return "Empty prompt."

        stream = body.get("stream", False)

        # 1) Prefer the local Hermes API server (OpenAI-compatible, true streaming).
        if _API_SERVER_KEY:
            try:
                if stream:
                    return self._stream_via_api(messages)
                return self._chat_via_api(messages)
            except Exception as e:
                print(f"[HermesPipe] API server call failed: {e}", file=sys.stderr)

        # 2) Otherwise use Hermes CLI with its default config (codex/gpt-5.5 if configured).
        #    If that fails, fall back to the explicit fallback provider.
        try:
            if stream:
                return self._stream_via_cli(user_prompt)
            return self._run_sync_cli(user_prompt)
        except Exception as e:
            print(f"[HermesPipe] Default CLI failed: {e}", file=sys.stderr)

        # 3) Last-resort fallback.
        try:
            if stream:
                return self._stream_via_cli(user_prompt, fallback=True)
            return self._run_sync_cli(user_prompt, fallback=True)
        except Exception as e:
            return f"HermesPipe error: {e}"

    # ------------------------------------------------------------------ API server

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {_API_SERVER_KEY}",
            "Content-Type": "application/json",
        }

    def _chat_via_api(self, messages: list) -> str:
        payload = {
            "model": _API_SERVER_MODEL,
            "messages": messages,
            "stream": False,
        }
        res = requests.post(_API_SERVER_URL, headers=self._build_headers(), json=payload, timeout=120)
        res.raise_for_status()
        data = res.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return _transform_actions_to_thinking(content) if content else "Hermes API returned empty content."

    def _stream_via_api(self, messages: list) -> Iterator[str]:
        payload = {
            "model": _API_SERVER_MODEL,
            "messages": messages,
            "stream": True,
        }

        with requests.post(
            _API_SERVER_URL,
            headers=self._build_headers(),
            json=payload,
            stream=True,
            timeout=120,
        ) as res:
            res.raise_for_status()

            for line in res.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data: "):
                    line = line[len("data: "):]
                if line == "[DONE]":
                    break

                try:
                    import json

                    chunk = json.loads(line)
                except Exception:
                    continue

                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                content = delta.get("content") or ""
                reasoning = delta.get("reasoning_content") or delta.get("reasoning") or ""

                if reasoning:
                    yield f"<think>{_strip_action_tags(reasoning)}</think>"

                if content:
                    yield _strip_action_tags(content)

    # ------------------------------------------------------------------ CLI

    def _build_cli_cmd(self, prompt: str, fallback: bool = False) -> list:
        hermes_path = os.environ.get("HERMES_PATH", "/root/.local/bin/hermes")
        cmd = [hermes_path, "-z", prompt, "--cli", "--yolo"]
        if fallback:
            cmd.extend(["--provider", _FALLBACK_PROVIDER, "-m", _FALLBACK_MODEL])
        return cmd

    def _run_cli(self, prompt: str, fallback: bool = False) -> str:
        env = {
            **os.environ,
            "PATH": "/root/.hermes/hermes-agent/venv/bin:" + os.environ.get("PATH", ""),
        }
        cmd = self._build_cli_cmd(prompt, fallback)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd="/root/.hermes/hermes-agent",
            env=env,
        )

        output = result.stdout.strip()
        if output:
            return output

        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise RuntimeError(f"Hermes error (code {result.returncode}): {stderr[:500]}")

        raise RuntimeError("Hermes returned empty response.")

    def _run_sync_cli(self, prompt: str, fallback: bool = False) -> str:
        try:
            output = self._run_cli(prompt, fallback)
            return _transform_actions_to_thinking(output)
        except FileNotFoundError:
            return "Hermes CLI not found. Please ensure Hermes is installed."
        except subprocess.TimeoutExpired:
            return "Hermes request timed out after 120 seconds."
        except Exception as e:
            return f"Error running Hermes: {str(e)}"

    def _stream_via_cli(self, prompt: str, fallback: bool = False) -> Iterator[str]:
        """Stream CLI output by chunking the transformed response."""
        try:
            output = self._run_cli(prompt, fallback)
        except FileNotFoundError:
            yield "Hermes CLI not found. Please ensure Hermes is installed."
            return
        except subprocess.TimeoutExpired:
            yield "Hermes request timed out after 120 seconds."
            return
        except Exception as e:
            yield f"Error running Hermes: {str(e)}"
            return

        transformed = _transform_actions_to_thinking(output)

        # Stream in small chunks so the UI animates token-by-token.
        chunk_size = 8
        for i in range(0, len(transformed), chunk_size):
            yield transformed[i:i + chunk_size]


if __name__ == "__main__":
    p = Pipe()
    sample = {"messages": [{"role": "user", "content": "hello"}]}
    print(p.pipe(sample))
