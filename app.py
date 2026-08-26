"""Aashiq Shaikh — offensive security portfolio.

Run the dev server:      python app.py
Build the static site:   python freeze.py
"""

import os
import re
from pathlib import Path

from flask import Flask, render_template, url_for
from markupsafe import Markup, escape

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


# ── Terminal transcripts ──────────────────────────────────────────────
# The recorded sessions on the salvo page are rendered here rather than in
# JavaScript, so a visitor with the script disabled still gets the whole
# transcript, already coloured. The player only decides *when* each line
# appears; what each line means is decided once, on the server.

# What kind of line this is. It sets the colour and, on the player, how long
# to dwell: a live result line is one nxc process finishing and should land
# like one, where a rule is instant.
_LINE_KINDS = (
    ("hit",  re.compile(r"^\[[^\]]{3,6}\]\s")),   # [ADMIN]  smb  10.0.0.10  DC01
    ("info", re.compile(r"^\[\*\]")),              # [*] salvo 1.0.0  |  nxc 1.5.0
    ("warn", re.compile(r"^\[!\]")),                # [!] LOCKOUT MATH - each ...
    ("bang", re.compile(r"^!{10,}\s*$")),          # the abort banner
    ("rule", re.compile(r"^\s*[=-]{10,}\s*$")),    # table rules
)

# Applied to the *escaped* line, so no pattern here may contain a raw '<'.
# Order matters: the longest and most specific alternative wins.
_TOKENS = re.compile(
    r"(?P<lock>LOCK!|STATUS_ACCOUNT_LOCKED_OUT)"
    r"|(?P<status>STATUS_[A-Z_]+)"
    r"|(?P<blocked>VALID\*)"
    r"|(?P<admin>\bADMIN\b|Pwn3d!)"
    r"|(?P<salvo>!CMD|\bn/a\b|\berr\b)"
    r"|(?P<exec>\bexec\b)"
    r"|(?P<ok>\bok\b)"
    r"|(?P<unk>(?<= )\?(?=\s|$))"
    r"|(?P<flag>(?<=\s)--?[A-Za-z][\w-]*)"
    r"|(?P<addr>\b(?:\d{1,3}\.){3}\d{1,3}\b)"
    r"|(?P<mark>&lt;$)"
)


def _line_kind(line):
    for name, pattern in _LINE_KINDS:
        if pattern.match(line):
            return name
    return "plain"


def _paint(line):
    """Wrap the verdict glyphs and flags in an already-escaped line."""
    return _TOKENS.sub(
        lambda m: '<b class="t-{}">{}</b>'.format(m.lastgroup, m.group()),
        str(escape(line)),
    )


@app.template_filter("terminal")
def terminal(text):
    """Captured terminal output as one block element per line.

    Block elements rather than newlines because the player hides lines it has
    not reached yet, and a hidden line has to take no space — otherwise the
    window opens as a column of blanks.
    """
    return Markup("".join(
        '<span class="tl k-{}">{}</span>'.format(_line_kind(line), _paint(line))
        for line in text.split("\n")
    ))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/salvo/")
def salvo():
    # The rail indexes the case: the problem, what the tool does, each claim,
    # the terminal it can all be checked in, and how to run it yourself.
    rail_nav = (
        [{"id": "problem", "label": "The problem"},
         {"id": "does", "label": "What it does"}]
        + [{"id": "claim-" + c["id"], "label": c["claim_short"]}
           for c in RESUME["salvo"]["claims"]]
        + [{"id": "shell", "label": "Run it"},
           {"id": "run", "label": "Run the evidence"}]
    )
    return render_template(
        "salvo.html",
        rail_nav=rail_nav,
        home_route="index",
        rail_role="salvo",
        # The terminal's opening run, rendered server-side so the section is
        # readable with no JavaScript, and the prompt string both the markup
        # and the engine echo.
        boot=RESUME["salvo"]["boot"],
        ps1="kali@kali:~$ ",
    )


@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
