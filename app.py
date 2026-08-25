"""Aashiq Shaikh — offensive security portfolio.

Run the dev server:      python app.py
Build the static site:   python freeze.py
"""

import os
from pathlib import Path

from flask import Flask, render_template

from data.resume import RESUME

app = Flask(__name__)

# Frozen-Flask writes the static build here; also what GitHub Pages publishes.
app.config["FREEZER_DESTINATION"] = "build"
app.config["FREEZER_RELATIVE_URLS"] = True


def _with_pdf_availability(credentials):
    """Flag credentials whose certificate PDF is actually on disk.

    The PDFs are binary and may not have made it into a given checkout, so the
    template hides the download rather than linking at a 404. Verification
    links always work — they point at the issuer.
    """
    files = Path(app.root_path) / "static"
    return [dict(c, pdf_available=(files / c["pdf"]).is_file()) for c in credentials]


@app.context_processor
def inject_resume():
    """Expose the resume data to every template without passing it in."""
    return {
        "r": RESUME,
        "profile": RESUME["profile"],
        "nav": RESUME["nav"],
        "credentials": _with_pdf_availability(RESUME["credentials"]),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
