"""Freeze the Flask app into plain HTML/CSS/JS in build/.

The output is fully static — open build/index.html directly, or publish the
directory to GitHub Pages, Netlify, or any web server.
"""

import shutil
from pathlib import Path

from flask_frozen import Freezer

from app import app

BUILD_DIR = Path(app.root_path) / "build"

freezer = Freezer(app)

if __name__ == "__main__":
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    freezer.freeze()
    # Stop GitHub Pages running the output through Jekyll, which would
    # otherwise drop any file or directory beginning with an underscore.
    (BUILD_DIR / ".nojekyll").touch()
    files = sum(1 for p in BUILD_DIR.rglob("*") if p.is_file())
    print(f"Static site written to {BUILD_DIR} ({files} files)")
