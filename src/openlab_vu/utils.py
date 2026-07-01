from datetime import datetime, UTC
from pathlib import Path

def ensure_dir(path: Path | str) -> Path:
    """
    Create a directory if it doesn't exist and
    return the resolved and expanded path.

    Args:
        path: A directory as a path or a string.

    Returns:
        The resolved and expanded path.
    """

    path = Path(path)
    path.mkdir(exist_ok=True, parents=True)
    return path.expanduser().resolve().absolute()


def iso_timestamp(
    fmt: str = "%Y-%m-%d_%H-%M-%S",
    ms: bool = False,
    split: bool = False,
) -> str | tuple[str, str]:
    """
    Create a datestamp and a timestamp as formatted strings.

    Args:
        fmt: Datetime format.
        ms: Use millisecond precision.
        split: Split the string into date and time components.

    Returns:
        The formatted date and time.
    """

    # Simplified ISO format (no timezone, etc.)
    end = None

    if ms:
        # Use ms precision
        fmt += "-%f"
        end = -3

    # Return (date, time).
    # UTC time is used to avoid ambiguity.
    ts = datetime.strftime(datetime.now(UTC), fmt)[:end]
    return ts.split("_") if split else ts
