# Portfolio — Aashiq Shaikh

Personal site for an offensive security practitioner. Built with **Python
(Flask + Jinja2)** and exported to a fully static site, so it runs as a dev
server locally and deploys anywhere that serves plain HTML.

## Structure

| Path | Purpose |
|---|---|
| `app.py` | Flask application, routes, and the `terminal` transcript filter |
| `data/resume.py` | All site content as Python data — the single source of truth |
| `data/demos.py` | Recorded salvo sessions and the capability tables the labs use |
| `templates/` | Jinja2 templates (`base.html`, `index.html`, `salvo.html`, `macros.html`) |
| `static/css/style.css` | The entire design system, tokens at the top |
| `static/js/main.js` | Progressive enhancement only |
| `static/js/salvo.js` | The salvo page's terminal player and three labs |
| `static/files/` | Certificate PDFs served as proof |
| `freeze.py` | Frozen-Flask build → static HTML in `build/` |

No JavaScript framework and no build toolchain. The page is fully readable with
JavaScript disabled — the scripts drive the rail position marker, the mobile
menu, entry animations, and the salvo page's player and labs, and nothing is
hidden until a script has confirmed it can reveal it again.

With scripting off, the salvo page loses playback and recalculation and keeps
every word: all six transcripts print in full, all ten verdict cards stack up,
the matrix cells become anchors into them, and both computed panels show the
real output they open on.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python app.py                    # http://127.0.0.1:5000
```

## Build the static site

```bash
python freeze.py                 # writes build/
```

`build/` is self-contained and uses relative URLs, so `build/index.html` opens
directly in a browser and the directory can be uploaded to any static host.

## Deploy to GitHub Pages

`.github/workflows/deploy.yml` builds and publishes on every push to `main`.
Enable it once:

**Repository → Settings → Pages → Build and deployment → Source: GitHub Actions**

The site publishes to `https://<username>.github.io/<repo>/`. The same `build/`
directory also drops straight into Netlify, Vercel, or Cloudflare Pages.

## Editing content

Everything on the page comes from `RESUME` in `data/resume.py`. Adding a
credential, a project, a skill group, or a phase of the engagement chain is a
data edit — the templates pick it up automatically. Section order and labels
come from the `nav` list in the same file.

Certificates are served from `static/files/`. To add one, drop the PDF there and
add an entry to `credentials` with its `verify` URL and `pdf` path.

## The salvo page

`/salvo/` makes a case for [salvo](https://github.com/aashiqoffortune-hash/salvo)
and then lets a reader check it: six recorded terminal sessions that replay, a
verdict matrix whose cells explain themselves, the lockout arithmetic with the
inputs left open, and `--dry-run` reimplemented in the browser.

### The recorded sessions

Every transcript in `data/demos.py` is real `salvo` output, not prose shaped to
look like a terminal. They were captured by running the tool against
`tests/fake_nxc.py` in salvo's own repository — a stand-in for NetExec that
emits genuine `nxc` line shapes for a fixed cast of hosts, and exposes the
switches that make the failure paths reproducible. To re-record:

```bash
git clone https://github.com/aashiqoffortune-hash/salvo.git && cd salvo
cp tests/fake_nxc.py /tmp/bin/nxc && chmod +x /tmp/bin/nxc && export PATH=/tmp/bin:$PATH

python3 salvo.py 10.0.0.10 10.0.0.11 -u jdoe -p 'Password123!' -d corp.local
FAKE_NXC_LOCKOUT=1 python3 salvo.py 10.0.0.10 10.0.0.11 -u jdoe -p 'Password123!' -d corp.local
FAKE_NXC_FAIL=1    python3 salvo.py 10.0.0.10 -u jdoe -p 'Password123!' -d corp.local -P smb,winrm
FAKE_NXC_DRIFT=1   python3 salvo.py --check-nxc -P smb,winrm,ldap,ssh
```

Paste the output into the matching `transcript` in `data/demos.py`. Column
alignment is load-bearing — the matrix is a fixed-width table — so the strings
are stored indented and straightened by `_d()` on import. `app.py`'s `terminal`
filter decides each line's colour and its dwell on playback; add a new glyph to
`_TOKENS` there and to the mirror of it at the top of `static/js/salvo.js`.

### The command builder

`BUILDER` in `data/demos.py` is a transcription of the capability tables at the
top of `salvo.py` — which nxc protocol parsers define `-d`, `--local-auth`, `-H`
and a per-protocol timeout flag. `salvo.js` builds command lines from them the
way `salvo --dry-run` does, so the panel is only honest while the two agree.
It was checked against the tool itself across nine input shapes — password and
hash, domain and local auth, both presets, awkward quoting, multiple targets —
and matched byte for byte. Re-check it after any change to those tables, and
after `salvo --check-nxc` reports drift against a newer NetExec.

## Design system

Tokens live at the top of `static/css/style.css`.

```css
--ink:   #100e0c;   /* warm near-black ground              */
--bone:  #eae4d9;   /* warm off-white text                 */
--sig:   #c8362c;   /* signal red — structural, not decor  */
--brass: #c99a4a;   /* reserved for verifiable credentials  */
```

The salvo page adds a second, narrower set — `--v-hot`, `--v-warm`, `--v-ok`,
`--v-held`, `--v-unk`, `--v-void`, `--v-self` — one per verdict bucket in the
tool. They exist because salvo's whole argument is that a cell has more than
two states, and a page cannot render that in two colours. Notably `--v-held`
is a colour and not a grey: greying a blocked-but-correct credential is the
exact mistake the tool was built to stop.

Type is `Archivo` (expanded, heavy) for display, `Newsreader` for narrative
prose, and `JetBrains Mono` for every label, tag and identifier.

One cascade rule matters when editing: `.inner` owns the horizontal gutter, so
section-level rules must set `padding-block` only. Setting shorthand `padding`
on `.section` or `.mast` silently cancels the gutter.
