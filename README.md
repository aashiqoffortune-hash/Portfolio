# Portfolio — Aashiq Shaikh

Personal site for an offensive security practitioner. Built with **Python
(Flask + Jinja2)** and exported to a fully static site, so it runs as a dev
server locally and deploys anywhere that serves plain HTML.

## Structure

| Path | Purpose |
|---|---|
| `app.py` | Flask application and routes |
| `data/resume.py` | All site content as Python data — the single source of truth |
| `templates/` | Jinja2 templates (`base.html`, `index.html`, `macros.html`) |
| `static/css/style.css` | The entire design system, tokens at the top |
| `static/js/main.js` | Progressive enhancement only |
| `static/files/` | Certificate PDFs served as proof |
| `freeze.py` | Frozen-Flask build → static HTML in `build/` |

No JavaScript framework and no build toolchain. The page is fully readable with
JavaScript disabled — the script only drives the rail position marker, the
mobile menu, and entry animations, and nothing is hidden until the script has
confirmed it can reveal it again.

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

## Design system

Tokens live at the top of `static/css/style.css`.

```css
--ink:   #100e0c;   /* warm near-black ground              */
--bone:  #eae4d9;   /* warm off-white text                 */
--sig:   #c8362c;   /* signal red — structural, not decor  */
--brass: #c99a4a;   /* reserved for verifiable credentials  */
```

Type is `Archivo` (expanded, heavy) for display, `Newsreader` for narrative
prose, and `JetBrains Mono` for every label, tag and identifier.

One cascade rule matters when editing: `.inner` owns the horizontal gutter, so
section-level rules must set `padding-block` only. Setting shorthand `padding`
on `.section` or `.mast` silently cancels the gutter.
