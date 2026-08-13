"""
Session Manager

Responsibilities:
1. Store User Queries
2. Store Responses
3. Retrieve Conversation History
4. Clear Session
"""

from typing import List, Dict


# In-memory session history
_session_history: List[Dict] = []


def store(query: str, answer: str) -> None:
    """
    Store a query-response pair.
    """

    _session_history.append(
        {
            "query": query,
            "answer": answer,
        }
    )


def get_history() -> List[Dict]:
    """
    Return the current session history.
    """

    return _session_history


def clear() -> None:
    """
    Clear the session history.
    """

    _session_history.clear()