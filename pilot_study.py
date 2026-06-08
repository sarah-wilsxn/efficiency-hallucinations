import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import aiohttp


def load_env_file(env_path: str = ".env") -> None:
    """Load simple KEY=VALUE pairs from a local .env file if it exists."""
    path = Path(env_path)
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()

# -----------------------------
# Configuration
# -----------------------------
# You can set these in your environment before running:
#   MODEL_GATEWAY_BASE_URL=https://your-model-gateway.example.com
#   MODEL_GATEWAY_API_KEY=your_api_key_here
#   MODEL_GATEWAY_MODELS=gpt-5.5-pro,claude-sonnet-4.5,gemini-3.5-flash,claude-opus-4.8,gpt-5.4-mini,gemini-3-flash-preview,gemini-3.1-pro-preview,gpt-5-mini,claude-opus-4.7-fast,qwen-3.5-122b-a10b,qwen-3.5-flash
#   MODEL_GATEWAY_CHAT_PATH=/v1/chat/completions
BASE_URL = os.getenv("MODEL_GATEWAY_BASE_URL", "https://your-model-gateway.example.com")
API_KEY = os.getenv("MODEL_GATEWAY_API_KEY", "YOUR_API_KEY_HERE")
DEFAULT_MODELS = [
    "gpt-5.5-pro",
    "claude-sonnet-4.5",
    "gemini-3.5-flash",
    "claude-opus-4.8",
    "gpt-5.4-mini",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gpt-5-mini",
    "claude-opus-4.7-fast",
    "qwen-3.5-122b-a10b",
    "qwen-3.5-flash",
]
MODELS = [
    model.strip()
    for model in os.getenv("MODEL_GATEWAY_MODELS", ",".join(DEFAULT_MODELS)).split(",")
    if model.strip()
]
CHAT_PATH = os.getenv("MODEL_GATEWAY_CHAT_PATH", "/v1/chat/completions")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("MODEL_GATEWAY_TIMEOUT", "90"))
MAX_CONCURRENT_REQUESTS_PER_MODEL = int(os.getenv("MODEL_GATEWAY_MAX_CONCURRENCY", "3"))
REQUEST_STAGGER_SECONDS = float(os.getenv("MODEL_GATEWAY_REQUEST_STAGGER_SECONDS", "0.5"))
MODEL_STAGGER_SECONDS = float(os.getenv("MODEL_GATEWAY_MODEL_STAGGER_SECONDS", "1.5"))
SLOW_REQUEST_TIMEOUT_SECONDS = float(os.getenv("MODEL_GATEWAY_SLOW_TIMEOUT", str(max(REQUEST_TIMEOUT_SECONDS, 90.0))))
SLOW_MODELS = {
    model.strip()
    for model in os.getenv("MODEL_GATEWAY_SLOW_MODELS", "").split(",")
    if model.strip()
}
RESULTS_DIR = Path(os.getenv("MODEL_GATEWAY_RESULTS_DIR", "results/pilot_study"))

MODEL_ALIASES = {
    "gpt-5.5-pro": "tokenrouter/gpt-5.5",
    "claude-sonnet-4.5": "anthropic/claude-sonnet-4.5",
    "qwen-3.5-flash": "qwen/qwen3.5-flash",
    "gemini-3.5-flash": "google/gemini-3.5-flash",
    "gemini-3-flash-preview": "google/gemini-3-flash-preview",
    "claude-opus-4.8": "anthropic/claude-opus-4.8",
    "claude-opus-4.7-fast": "anthropic/claude-opus-4.7-fast",
    "gemini-3.1-pro-preview": "google/gemini-3.1-pro-preview",
    "gpt-5.4-mini": "openai/gpt-5.4-mini",
    "gpt-5-mini": "openai/gpt-5-mini",
    "qwen-3.5-122b-a10b": "qwen/qwen3.5-122b-a10b",
}

CONTROL_PROMPT_TEMPLATE = "Optimize this code for execution speed:\n\n{code}"
IIV_PENALTY_PROMPT_TEMPLATE = (
    "Optimize this code for execution speed. "
    "Only suggest an edit if you are >90% certain it improves execution speed; "
    "otherwise, output exactly 'Already Optimal'.\n\n{code}"
)

# -----------------------------
# Pilot Dataset
# -----------------------------
SNIPPETS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "type": "sub-optimal",
        "code": """class Solution:\n    def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:\n        # Sub-optimal: Exponential brute-force recursion without pruning\n        ans = []\n        def dfs(idx, current_path, current_sum):\n            if current_sum == target:\n                if sorted(current_path) not in ans:\n                    ans.append(sorted(current_path))\n                return\n            if current_sum > target or idx >= len(candidates):\n                return\n            for i in range(idx, len(candidates)):\n                dfs(i + 1, current_path + [candidates[i]], current_sum + candidates[i])\n        dfs(0, [], 0)\n        return ans\n""",
    },
    {
        "id": 2,
        "type": "sub-optimal",
        "code": """class Solution:\n    def removeDuplicates(self, nums: List[int]) -> int:\n        # Sub-optimal: O(n^2) approach using repeated list popping\n        i = 0\n        while i < len(nums):\n            if nums.count(nums[i]) > 2:\n                nums.pop(i)\n            else:\n                i += 1\n        return len(nums)\n""",
    },
    {
        "id": 3,
        "type": "sub-optimal",
        "code": """class Solution:\n    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:\n        # Sub-optimal: String serialization comparison instead of structural recursion\n        def serialize(root):\n            if not root: return \"None\"\n            return f\"{root.val},{serialize(root.left)},{serialize(root.right)}\"\n        return serialize(p) == serialize(q)\n""",
    },
    {
        "id": 4,
        "type": "sub-optimal",
        "code": """class Solution:\n    def findEvenNumbers(self, digits: List[int]) -> List[int]:\n        # Sub-optimal: O(n^3) nested loop checking all digit combinations permutations\n        ans = set()\n        n = len(digits)\n        for i in range(n):\n            for j in range(n):\n                for k in range(n):\n                    if i != j and j != k and i != k:\n                        val = digits[i] * 100 + digits[j] * 10 + digits[k]\n                        if val >= 100 and val % 2 == 0:\n                            ans.add(val)\n        return sorted(list(ans))\n""",
    },
    {
        "id": 5,
        "type": "sub-optimal",
        "code": """class Solution:\n    def minOperations(self, n: int) -> int:\n        # Sub-optimal: Naive simulation decrementing step-by-step instead of bit shifting\n        ans = 0\n        curr = n\n        while curr > 0:\n            if curr % 2 == 1:\n                curr -= 1\n            else:\n                curr //= 2\n            ans += 1\n        return ans\n""",
    },
    {
        "id": 6,
        "type": "optimal",
        "code": """class Solution:\n    def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:\n        def dfs(i: int, s: int):\n            if s == 0:\n                ans.append(t[:])\n                return\n            if i >= len(candidates) or s < candidates[i]:\n                return\n            for j in range(i, len(candidates)):\n                if j > i and candidates[j] == candidates[j - 1]:\n                    continue\n                t.append(candidates[j])\n                dfs(j + 1, s - candidates[j])\n                t.pop()\n\n        candidates.sort()\n        ans = []\n        t = []\n        dfs(0, target)\n        return ans\n""",
    },
    {
        "id": 7,
        "type": "optimal",
        "code": """class Solution:\n    def removeDuplicates(self, nums: List[int]) -> int:\n        k = 0\n        for x in nums:\n            if k < 2 or x != nums[k - 2]:\n                nums[k] = x\n                k += 1\n        return k\n""",
    },
    {
        "id": 8,
        "type": "optimal",
        "code": """class Solution:\n    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:\n        if p == q:\n            return True\n        if p is None or q is None or p.val != q.val:\n            return False\n        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)\n""",
    },
    {
        "id": 9,
        "type": "optimal",
        "code": """class Solution:\n    def findEvenNumbers(self, digits: List[int]) -> List[int]:\n        ans = []\n        counter = Counter(digits)\n        for i in range(100, 1000, 2):\n            t = []\n            k = i\n            while k:\n                t.append(k % 10)\n                k //= 10\n            cnt = Counter(t)\n            if all([counter[i] >= cnt[i] for i in range(10)]):\n                ans.append(i)\n        return ans\n""",
    },
    {
        "id": 10,
        "type": "optimal",
        "code": """class Solution:\n    def minOperations(self, n: int) -> int:\n        ans = cnt = 0\n        while n:\n            if n & 1:\n                cnt += 1\n            elif cnt:\n                ans += 1\n                cnt = 0 if cnt == 1 else 1\n            n >>= 1\n        if cnt == 1:\n            ans += 1\n        elif cnt > 1:\n            ans += 2\n        return ans\n""",
    },
]


PROMPT_CONDITIONS = {
    "control": CONTROL_PROMPT_TEMPLATE,
    "iiv_penalty": IIV_PENALTY_PROMPT_TEMPLATE,
}


def build_url(base_url: str, path: str) -> str:
    normalized_base = base_url.rstrip("/")
    normalized_path = path.lstrip("/")

    if normalized_base.endswith("/v1") and normalized_path.startswith("v1/"):
        normalized_path = normalized_path[3:]

    return f"{normalized_base}/{normalized_path}"


def resolve_model_name(requested_model: str, available_models: set[str]) -> str | None:
    candidate = MODEL_ALIASES.get(requested_model, requested_model)
    if candidate in available_models:
        return candidate
    return None


async def fetch_available_models(
    session: aiohttp.ClientSession,
    endpoint_url: str,
    headers: Dict[str, str],
) -> set[str]:
    try:
        async with session.get(endpoint_url, headers=headers) as resp:
            if resp.status >= 400:
                return set()
            payload = await resp.json()
    except Exception:
        return set()

    models = payload.get("data", []) if isinstance(payload, dict) else []
    if not isinstance(models, list):
        return set()

    available_models: set[str] = set()
    for item in models:
        if isinstance(item, dict):
            model_id = item.get("id")
            if isinstance(model_id, str):
                available_models.add(model_id)

    return available_models


def extract_response_text(payload: Dict[str, Any]) -> str:
    """Extract model text across common chat-completion response shapes."""
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message") if isinstance(first, dict) else None
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict) and isinstance(item.get("text"), str):
                        parts.append(item["text"])
                if parts:
                    return "\n".join(parts)

        text = first.get("text") if isinstance(first, dict) else None
        if isinstance(text, str):
            return text

    output_text = payload.get("output_text")
    if isinstance(output_text, str):
        return output_text

    return f"[Unrecognized response schema] {str(payload)[:500]}"


def classify_behavior(code_type: str, condition: str, response_text: str) -> str:
    trimmed = response_text.strip()
    already_optimal = trimmed == "Already Optimal"

    if condition == "iiv_penalty" and already_optimal and code_type == "optimal":
        return "Calibrated abstention"
    if condition == "iiv_penalty" and already_optimal and code_type == "sub-optimal":
        return "Potential false abstention"
    if condition == "iiv_penalty" and not already_optimal and code_type == "optimal":
        return "Potential over-edit"
    if condition == "iiv_penalty" and not already_optimal and code_type == "sub-optimal":
        return "Action on improvable code"
    if condition == "control" and already_optimal:
        return "Unexpected abstention (control)"
    if condition == "control" and not already_optimal:
        return "Edit suggested (control)"
    return "Unclassified"


def latex_escape(text: str) -> str:
    """Escape LaTeX special characters."""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def preview_text(text: str, max_len: int = 120) -> str:
    one_line = " ".join(text.split())
    if len(one_line) <= max_len:
        return one_line
    return one_line[: max_len - 3] + "..."


def safe_filename(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in name)


async def call_model(
    session: aiohttp.ClientSession,
    snippet: Dict[str, Any],
    condition_name: str,
    prompt_template: str,
    endpoint_url: str,
    headers: Dict[str, str],
    model_name: str,
    semaphore: asyncio.Semaphore,
    delay_seconds: float = 0.0,
    request_timeout: aiohttp.ClientTimeout | None = None,
) -> Dict[str, Any]:
    prompt = prompt_template.format(code=snippet["code"])
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }

    try:
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)
        async with semaphore:
            try:
                async with session.post(endpoint_url, headers=headers, json=payload, timeout=request_timeout) as resp:
                    text_body = await resp.text()
                    if resp.status >= 400:
                        response_text = f"[HTTP {resp.status}] {text_body[:500]}"
                    else:
                        try:
                            json_body = await resp.json()
                            response_text = extract_response_text(json_body)
                        except Exception:
                            response_text = f"[Non-JSON response] {text_body[:500]}"
            except asyncio.TimeoutError:
                response_text = "[Timeout] Request exceeded configured timeout"
            except aiohttp.ClientError as exc:
                response_text = f"[Network error] {type(exc).__name__}: {exc}"
            except Exception as exc:
                response_text = f"[Unexpected error] {type(exc).__name__}: {exc}"
    except Exception as exc:
        response_text = f"[Unexpected semaphore error] {type(exc).__name__}: {exc}"

    behavior = classify_behavior(snippet["type"], condition_name, response_text)

    return {
        "id": snippet["id"],
        "model": model_name,
        "code_type": snippet["type"],
        "prompt_condition": condition_name,
        "response": response_text,
        "response_preview": preview_text(response_text),
        "behavioral_classification": behavior,
    }


async def run_model_batch(
    session: aiohttp.ClientSession,
    requested_model: str,
    model_name: str,
    endpoint_url: str,
    headers: Dict[str, str],
    timeout_seconds: float,
) -> List[Dict[str, Any]]:
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    semaphore = asyncio.Semaphore(max(1, MAX_CONCURRENT_REQUESTS_PER_MODEL))
    tasks = []
    request_index = 0

    for snippet in SNIPPETS:
        for condition_name, template in PROMPT_CONDITIONS.items():
            tasks.append(
                call_model(
                    session=session,
                    snippet=snippet,
                    condition_name=condition_name,
                    prompt_template=template,
                    endpoint_url=endpoint_url,
                    headers=headers,
                    model_name=model_name,
                    semaphore=semaphore,
                    delay_seconds=request_index * REQUEST_STAGGER_SECONDS,
                    request_timeout=timeout,
                )
            )
            request_index += 1

    try:
        return await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout.total + 15)
    except asyncio.TimeoutError:
        results: List[Dict[str, Any]] = []
        for snippet in SNIPPETS:
            for condition_name in PROMPT_CONDITIONS:
                timeout_text = "[Timeout] Model run exceeded per-model timeout"
                results.append(
                    {
                        "id": snippet["id"],
                        "model": model_name,
                        "code_type": snippet["type"],
                        "prompt_condition": condition_name,
                        "response": timeout_text,
                        "response_preview": preview_text(timeout_text),
                        "behavioral_classification": classify_behavior(
                            snippet["type"], condition_name, timeout_text
                        ),
                    }
                )
        return results


def print_terminal_results(results: List[Dict[str, Any]]) -> None:
    print("\n=== Pilot Study Results (Terminal View) ===")
    for row in results:
        print("-" * 80)
        print(f"ID: {row['id']}")
        print(f"Model: {row['model']}")
        print(f"Code Type: {row['code_type']}")
        print(f"Prompt Condition: {row['prompt_condition']}")
        print(f"Behavioral Classification: {row['behavioral_classification']}")
        print(f"Response Preview: {row['response_preview']}")


def print_latex_tabular(results: List[Dict[str, Any]]) -> None:
    print("\n=== LaTeX Tabular Output ===")
    print("\\begin{tabular}{r l l l p{7.2cm} l}")
    print("\\hline")
    print("ID & Model & Code Type & Prompt Condition & Model Response Preview & Behavioral Classification \\\\")
    print("\\hline")

    for row in results:
        line = (
            f"{row['id']}"
            f" & {latex_escape(row['model'])}"
            f" & {latex_escape(row['code_type'])}"
            f" & {latex_escape(row['prompt_condition'])}"
            f" & {latex_escape(row['response_preview'])}"
            f" & {latex_escape(row['behavioral_classification'])} \\\\")
        print(line)

    print("\\hline")
    print("\\end{tabular}")


async def main() -> None:
    if len(SNIPPETS) != 10:
        raise ValueError(f"Expected exactly 10 snippets, found {len(SNIPPETS)}")
    if not MODELS:
        raise ValueError("No models configured. Set MODEL_GATEWAY_MODELS or update DEFAULT_MODELS.")

    endpoint_url = build_url(BASE_URL, CHAT_PATH)
    models_url = build_url(BASE_URL, "models")
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    combined_results: List[Dict[str, Any]] = []

    async with aiohttp.ClientSession(timeout=timeout) as session:
        available_models = await fetch_available_models(session, models_url, headers)
        if available_models:
            print(f"\nDiscovered {len(available_models)} available gateway models.")
        else:
            print("\nCould not discover gateway models; using the configured model list as-is.")

        resolved_models: List[tuple[str, str]] = []
        skipped_models: List[str] = []
        for requested_model in MODELS:
            resolved_model = resolve_model_name(requested_model, available_models) if available_models else requested_model
            if resolved_model:
                resolved_models.append((requested_model, resolved_model))
            else:
                skipped_models.append(requested_model)

        if skipped_models:
            print("Skipping unavailable models:")
            for model_name in skipped_models:
                print(f"- {model_name}")

        fast_models = []
        slow_models = []
        for requested_model, model_name in resolved_models:
            if requested_model in SLOW_MODELS or model_name in SLOW_MODELS:
                slow_models.append((requested_model, model_name))
            else:
                fast_models.append((requested_model, model_name))

        for requested_model, model_name in fast_models + slow_models:
            model_results_path = RESULTS_DIR / f"{safe_filename(requested_model)}.json"
            if model_results_path.exists():
                print(f"\n=== Skipping already computed model: {requested_model} ===")
                continue

            print(f"\n=== Running model: {requested_model} -> {model_name} ===")
            if MODEL_STAGGER_SECONDS > 0:
                await asyncio.sleep(MODEL_STAGGER_SECONDS)
            per_model_timeout = SLOW_REQUEST_TIMEOUT_SECONDS if requested_model in SLOW_MODELS or model_name in SLOW_MODELS else REQUEST_TIMEOUT_SECONDS
            results = await run_model_batch(
                session=session,
                requested_model=requested_model,
                model_name=model_name,
                endpoint_url=endpoint_url,
                headers=headers,
                timeout_seconds=per_model_timeout,
            )

            condition_order = {"control": 0, "iiv_penalty": 1}
            results.sort(key=lambda r: (r["id"], condition_order.get(r["prompt_condition"], 99)))

            with model_results_path.open("w", encoding="utf-8") as handle:
                json.dump(results, handle, indent=2, ensure_ascii=False)

            combined_results.extend(results)
            print_terminal_results(results)
            print_latex_tabular(results)

    combined_results = []
    requested_result_files = {f"{safe_filename(model)}.json" for model in MODELS}
    for result_path in sorted(RESULTS_DIR.glob("*.json")):
        if result_path.name == "pilot_study_all_models.json":
            continue
        if result_path.name not in requested_result_files:
            continue
        with result_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
            if isinstance(payload, list):
                combined_results.extend(payload)

    combined_results.sort(key=lambda r: (r.get("model", ""), r.get("id", 0), r.get("prompt_condition", "")))

    combined_results_path = RESULTS_DIR / "pilot_study_all_models.json"
    with combined_results_path.open("w", encoding="utf-8") as handle:
        json.dump(combined_results, handle, indent=2, ensure_ascii=False)

    print(f"\nSaved per-model results to: {RESULTS_DIR}")
    print(f"Saved combined results to: {combined_results_path}")


if __name__ == "__main__":
    asyncio.run(main())