# Import from canonical root AzazaelDynamicLogger
import sys
from pathlib import Path
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)
_root_src = str(Path(__file__).resolve().parent.parent.parent)  # src/
if _root_src not in sys.path:
    sys.path.insert(0, _root_src)

