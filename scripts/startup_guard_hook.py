"""Custom PyInstaller runtime hook: run BEFORE the bundled Qt runtime hook."""
import os
import sys

from launcher import GUARD_ENV, WORKER_FLAG, run

if not (len(sys.argv) > 1 and sys.argv[1] == WORKER_FLAG and os.environ.get(GUARD_ENV)):
    raise SystemExit(run())
