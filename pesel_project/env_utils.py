from typing import Iterable, List, Optional
import os


def _get_env_raw(key: str) -> Optional[str]:
    return os.environ.get(key)


def env_str(key: str, default: Optional[str] = None, required: bool = False) -> str:
    value = _get_env_raw(key)
    if value is None or value == "":
        if required and default is None:
            raise RuntimeError(f"Missing required environment variable: {key}")
        return default  # type: ignore[return-value]
    return value


def env_bool(key: str, default: Optional[bool] = None) -> bool:
    raw = _get_env_raw(key)
    if raw is None or raw == "":
        if default is None:
            return False
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    return True


def env_int(key: str, default: Optional[int] = None) -> int:
    raw = _get_env_raw(key)
    if raw is None or raw == "":
        if default is None:
            raise RuntimeError(f"Missing required integer environment variable: {key}")
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid integer for environment variable {key}: {raw}") from exc


def env_list(
    key: str,
    default: Optional[Iterable[str]] = None,
    separator: str = ",",
) -> List[str]:
    raw = _get_env_raw(key)
    if raw is None or raw.strip() == "":
        return list(default) if default is not None else []
    return [item.strip() for item in raw.split(separator) if item.strip() != ""]
