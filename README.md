# Portfolio — Aashiq Shaikh

Personal site for an offensive security practitioner. Built with **Python
(Flask + Jinja2)** and exported to a fully static site, so it runs as a dev
server locally and deploys anywhere that serves plain HTML.

## Structure

| Path | Purpose |
|---|---|
| `app.py` | Flask application, routes, and the `terminal` transcript filter |
| `data/resume.py` | All site content as Python data — the single source of truth |
| `data/demos.py` | The estate the salvo terminal answers for, and nxc's capability tables |
| `templates/` | Jinja2 templates (`base.html`, `index.html`, `salvo.html`, `macros.html`) |
| `static/css/style.css` | The entire design system, tokens at the top |
| `static/js/main.js` | Progressive enhancement only |
| `static/js/salvo.js` | The salvo page's terminal — a working salvo in the browser |
| `static/files/` | Certificate PDFs served as proof |
| `freeze.py` | Frozen-Flask build → static HTML in `build/` |

No JavaScript framework and no build toolchain. The page is fully readable with
JavaScript disabled — the scripts drive the rail position marker, the mobile
menu, entry animations, and the salvo page's terminal, and nothing is hidden
until a script has confirmed it can reveal it again.

With scripting off, the salvo page loses the prompt and keeps every word: the
terminal renders one real recorded run in full, already coloured.

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
and then lets a reader check it in a terminal. Not a recording and not a mock:
type a command and the page parses the arguments, plans the jobs, resolves each
one against a fixed six-host estate, and prints the matrix.

```
kali@kali:~$ salvo 10.0.0.0/24 -u jdoe -p 'Password123!' -d corp.local
kali@kali:~$ salvo 10.0.0.42 -u root -p toor -P ssh,ftp,smb
kali@kali:~$ salvo --dry-run ...      --selftest    --check-nxc    --legend
kali@kali:~$ help        hosts        creds         clear
```

Arrow keys walk the history, Tab completes, and any command printed on screen
runs when clicked.

### Why it can be trusted

`static/js/salvo.js` is a port of the parts of `salvo.py` that decide what a
cell means — the verdict buckets, the NT status map, the severity order, what
`Pwn3d!` proves per protocol, and the nxc capability tables. A port can drift,
so it is tested rather than asserted:

1. `ESTATE` in `data/demos.py` defines the network.
2. A NetExec stand-in serves that same estate to the real `salvo`, in genuine
   nxc line shapes.
3. Real salvo is run against it and the output kept as ground truth.
4. The page is driven in a headless browser and its output diffed against that,
   across every command shape the terminal accepts — password and hash, domain
   and local auth, a wrong password, a lockout, a host with nothing listening.

Nine cases, matching line for line, including the advisories salvo prints when
a protocol cannot take the credential it was handed. Re-run that diff after any
change to the engine or the tables, and after `salvo --check-nxc` reports drift
against a newer NetExec.

`BOOT` is one of those real runs, kept verbatim as the no-JavaScript content of
the section. `app.py`'s `terminal` filter colours it server-side; the engine
mirrors the same token rules so a line it prints and a line Jinja rendered look
identical. Add a glyph to `_TOKENS` in `app.py` and to `TOKENS` in `salvo.js`
together, or the two will disagree.

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
