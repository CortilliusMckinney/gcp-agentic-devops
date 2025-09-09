# ============================================
# 🧾 logging_utils.py (Improved for Readability)
# Clean, scannable log blocks that prioritize the important information
# and minimize noise for production environments.
# ============================================

from __future__ import annotations
import json
from typing import Iterable, Optional, Dict, Any


def log_block(
    agent: str,
    title: str,
    lines: Optional[Iterable[str]] = None,
    mini: Optional[Dict[str, Any]] = None,
    simple: bool = False,  # NEW: Simple mode for less verbose output
) -> None:
    """
    Clean log block optimized for Cloud Functions readability.

    agent: e.g. "🧠 [Diagnoser]" or "🛠️ [Remediator]"
    title: e.g. "Event received", "Diagnosis ready"
    lines: key information to display
    mini: compact JSON for essential data
    simple: if True, uses single-line format for brevity
    """

    if simple:
        # Single-line format for key events
        header = f"{agent} {title}"
        if lines:
            details = " | ".join(str(line).strip() for line in lines if line)
            print(f"{header} | {details}")
        else:
            print(header)
        return

    # Multi-line format for detailed events
    buf = [f"{agent} {title}"]

    if lines:
        for line in lines:
            if line and str(line).strip():
                print(f"  • {str(line).strip()}")

    # Add mini JSON on separate line if provided
    if mini:
        try:
            compact = json.dumps(mini, separators=(",", ":"))
            print(f"  → {compact}")
        except Exception:
            pass

    print()  # Blank line for readability


def log_simple(agent: str, message: str) -> None:
    """Ultra-simple one-liner for basic events."""
    print(f"{agent} {message}")


def log_error(agent: str, error: str) -> None:
    """Clean error logging."""
    print(f"❌ {agent} ERROR: {error}")


def log_success(agent: str, message: str, details: Optional[str] = None) -> None:
    """Success with optional details."""
    print(f"✅ {agent} {message}")
    if details:
        print(f"  → {details}")
    print()


# ============================================
# 🎯 Usage Examples:
#
# # Simple events
# log_simple("🧠 [Diagnoser]", "Event received (Cloudflare)")
#
# # Detailed events
# log_block("🧠 [Diagnoser]", "Diagnosis ready",
#          lines=["React 18 dependency conflict detected"])
#
# # Success events
# log_success("🧠 [Diagnoser]", "Published to diagnosis-events",
#            "Message ID: 123456")
#
# # Errors
# log_error("🧠 [Diagnoser]", "Failed to parse event data")
# ============================================
