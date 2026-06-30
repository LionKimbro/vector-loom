"""Launch the standalone Vector Loom viewer without installing the package.

    python run_viewer.py examples/folder_node.vloom.json
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from vectorloom.viewer import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
