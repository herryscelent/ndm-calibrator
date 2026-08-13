"""Background computation workers (QThread) with cancellation support.

The GUI must never freeze during identification/bootstrap; all long-running
numeric work runs in a QThread and reports progress via signals.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Dict, Optional

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)

_CANCEL_EVENTS: Dict[int, threading.Event] = {}
_CANCEL_LOCK = threading.Lock()


class _Cancellable:
    """Cooperative cancellation token checked by long-running loops."""

    def __init__(self):
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def cancelled(self) -> bool:
        return self._event.is_set()


class RunWorker(QThread):
    """Runs a callable in a worker thread with a cancellation token.

    ``fn`` receives a ``CancellationToken`` as its only argument; it should
    check ``token.cancelled()`` periodically and raise `CancelledError` or
    return early when cancelled.
    """

    finished_ok = Signal(object)
    finished_error = Signal(str)
    progress = Signal(str)

    def __init__(self, fn: Callable, parent=None):
        super().__init__(parent)
        self._fn = fn
        self._token = _Cancellable()

    def run(self) -> None:
        try:
            result = self._fn(self._token)
            self.finished_ok.emit(result)
        except CancelledError:
            self.finished_error.emit("操作已取消")
        except Exception as exc:  # surface to GUI, never crash
            logger.exception("后台任务失败")
            self.finished_error.emit(str(exc))

    def cancel(self) -> None:
        self._token.cancel()


class CancelledError(Exception):
    """Raised inside a worker when the user cancels the run."""
