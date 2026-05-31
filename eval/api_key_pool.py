import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = "https://batch.dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_KEY_COOLDOWN_SECONDS = 300.0


KEY_ERROR_STATUSES = {401, 403, 429}
KEY_ERROR_MARKERS = (
    "api key",
    "apikey",
    "authentication",
    "authorization",
    "unauthorized",
    "quota",
    "rate limit",
    "too many requests",
    "access denied",
)


@dataclass(frozen=True)
class ApiKeyLease:
    index: int
    api_key: str
    label: str


@dataclass
class _ApiKeyState:
    api_key: str
    cooldown_until: float = 0.0
    failure_count: int = 0


class ApiKeyPool:
    def __init__(self, api_keys: list[str]) -> None:
        if not api_keys:
            raise ValueError("ApiKeyPool requires at least one API key.")
        self._states = [_ApiKeyState(api_key=api_key) for api_key in api_keys]
        self._index = 0
        self._lock = threading.Lock()
        self._cooldown_seconds = _read_float_env(
            "OPENAI_API_KEY_COOLDOWN_SECONDS",
            DEFAULT_KEY_COOLDOWN_SECONDS,
        )

    @property
    def size(self) -> int:
        return len(self._states)

    def next_key(self) -> ApiKeyLease:
        while True:
            with self._lock:
                now = time.monotonic()
                for _ in range(len(self._states)):
                    key_index = self._index % len(self._states)
                    self._index += 1
                    state = self._states[key_index]
                    if state.cooldown_until <= now:
                        return self._lease_for(key_index)

                next_ready_at = min(state.cooldown_until for state in self._states)
                wait_seconds = max(0.1, min(next_ready_at - now, 5.0))

            time.sleep(wait_seconds)

    def report_success(self, lease: ApiKeyLease) -> None:
        with self._lock:
            state = self._states[lease.index]
            state.failure_count = 0

    def report_failure(
        self,
        lease: ApiKeyLease,
        status_code: int | None = None,
        error_text: str | None = None,
    ) -> str | None:
        if not _is_key_related_error(status_code, error_text):
            return None

        with self._lock:
            state = self._states[lease.index]
            state.failure_count += 1
            multiplier = min(8, 2 ** max(0, state.failure_count - 1))
            cooldown_seconds = self._cooldown_seconds * multiplier
            state.cooldown_until = max(
                state.cooldown_until,
                time.monotonic() + cooldown_seconds,
            )
            return (
                f"Cooling down API key {lease.label} for "
                f"{int(cooldown_seconds)}s after status {status_code or 'unknown'}."
            )

    def _lease_for(self, key_index: int) -> ApiKeyLease:
        api_key = self._states[key_index].api_key
        return ApiKeyLease(
            index=key_index,
            api_key=api_key,
            label=_mask_key(key_index, api_key),
        )


def _read_float_env(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _mask_key(index: int, api_key: str) -> str:
    suffix = api_key[-4:] if len(api_key) >= 4 else "****"
    return f"#{index + 1}(...{suffix})"


def _is_key_related_error(status_code: int | None, error_text: str | None) -> bool:
    if status_code in KEY_ERROR_STATUSES:
        return True
    lowered = (error_text or "").lower()
    return any(marker in lowered for marker in KEY_ERROR_MARKERS)


def resolve_base_url() -> str:
    return os.environ.get("OPENAI_BASE_URL") or DEFAULT_BASE_URL


def resolve_key_file(path_str: str | None) -> Path | None:
    if not path_str:
        return None
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _parse_key_line(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "=" in stripped:
        stripped = stripped.split("=", 1)[1].strip()
    stripped = stripped.strip("'\"")
    return stripped or None


def _read_key_file(path: Path) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        api_key = _parse_key_line(line)
        if api_key and api_key not in seen:
            keys.append(api_key)
            seen.add(api_key)
    return keys


def _default_key_file_candidates() -> list[Path]:
    candidates = [PROJECT_ROOT / "key", PROJECT_ROOT.parent / "key"]
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved not in seen:
            unique.append(path)
            seen.add(resolved)
    return unique


def load_api_key_pool() -> tuple[ApiKeyPool, str]:
    explicit_key_file = resolve_key_file(
        os.environ.get("OPENAI_API_KEYS_FILE") or os.environ.get("OPENAI_API_KEY_FILE")
    )
    key_files = [explicit_key_file] if explicit_key_file else _default_key_file_candidates()

    for key_file in key_files:
        if key_file is None or not key_file.exists():
            continue
        keys = _read_key_file(key_file)
        if keys:
            return ApiKeyPool(keys), str(key_file)
        if explicit_key_file:
            raise EnvironmentError(f"No API keys found in explicit key file: {key_file}")

    env_api_key = os.environ.get("OPENAI_API_KEY")
    if env_api_key:
        return ApiKeyPool([env_api_key]), "OPENAI_API_KEY"

    checked = ", ".join(str(path) for path in key_files if path is not None)
    raise EnvironmentError(
        "No API keys found. Put one key per line in a key file "
        f"({checked}) or set OPENAI_API_KEY."
    )
