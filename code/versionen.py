"""Frechenlehen – plan versions (issue #59, ADR-005-JXWL; pure Python + git, standard library only).

A version is a frozen state of the plan: an id (its date, YYYY-MM-DD, unique), a name and a snapshot
of the committed sources, `versionen/<id>.tar.gz` (`git archive HEAD code plans`), listed in
`versionen/versionen.json`. A snapshot never changes once committed.

- freeze(repo, name, id): writes the snapshot and the entry (refuses uncommitted code/ or plans/ and
  an existing id).
- build(repo, public, cache): per version `public/v/<id>/frechenlehen.glb`, exported by the
  snapshot's own code/export_gltf.py, and `public/v/<id>/plans/*.svg` from the snapshot; cached per
  snapshot hash in `cache/<id>-<sha12>/`; plus `public/versionen.json` (newest first) for the viewer.

CLI:  versionen.py freeze <name> [--id YYYY-MM-DD]  |  versionen.py build <public dir>
"""
import datetime, filecmp, hashlib, json, re, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIST = Path("versionen") / "versionen.json"
SOURCES = ("code", "plans")
ID = re.compile(r"\d{4}-\d{2}-\d{2}")


def load(repo):
    """The listed versions, [{id, name}], sorted by id (oldest first)."""
    p = Path(repo) / LIST
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def freeze(repo, name, vid):
    """Snapshot the committed code/ and plans/ as version `vid`; returns the snapshot's path."""
    repo = Path(repo)
    if not ID.fullmatch(vid):
        raise ValueError(f"id {vid!r} is not YYYY-MM-DD")
    if not name.strip():
        raise ValueError("a version needs a name")
    listed = load(repo)
    if any(v["id"] == vid for v in listed):
        raise ValueError(f"version {vid} exists")
    dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", *SOURCES],
                           check=True, capture_output=True, text=True).stdout
    if dirty.strip():
        raise ValueError("uncommitted changes in code/ or plans/: commit them first\n" + dirty)
    snap = repo / "versionen" / f"{vid}.tar.gz"
    snap.parent.mkdir(exist_ok=True)
    subprocess.run(["git", "-C", str(repo), "archive", "--format=tar.gz", "-o", str(snap), "HEAD", *SOURCES],
                   check=True)
    listed.append({"id": vid, "name": name.strip()})
    listed.sort(key=lambda v: v["id"])
    (repo / LIST).write_text(json.dumps(listed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return snap


def _export(snap, out):
    """Unpack the snapshot and run its own exporter: out/frechenlehen.glb, out/plans/*.svg."""
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(snap) as t:
            t.extractall(tmp, filter="data")
        work = Path(tmp) / "out"
        subprocess.run([sys.executable, str(Path(tmp) / "code" / "export_gltf.py"), str(work / "frechenlehen.glb")],
                       check=True, cwd=tmp, stdout=subprocess.DEVNULL)
        shutil.copytree(Path(tmp) / "plans", work / "plans")
        shutil.rmtree(out, ignore_errors=True)
        shutil.move(work, out)                     # whole or not at all: an interrupted build re-exports


def _same(a, b):
    """True when directory b holds exactly a's files with a's bytes."""
    files = lambda d: sorted(p.relative_to(d) for p in d.rglob("*") if p.is_file())
    return b.is_dir() and files(a) == files(b) and all(filecmp.cmp(a / f, b / f, shallow=False) for f in files(a))


def build(repo, public, cache):
    """Every listed version into public/v/<id>/ (from the cache where it is; an unchanged version is
    left alone, an unlisted one removed); returns the exports run."""
    repo, public, cache = Path(repo), Path(public), Path(cache)
    listed, exported = load(repo), 0
    for v in listed:
        if not ID.fullmatch(v["id"]):                      # a hand-edited list: never a path
            raise ValueError(f"id {v['id']!r} is not YYYY-MM-DD")
    for old in (public / "v").glob("*") if (public / "v").is_dir() else []:
        if old.name not in {v["id"] for v in listed}:
            shutil.rmtree(old)
    for v in listed:
        snap = repo / "versionen" / f"{v['id']}.tar.gz"
        built = cache / f"{v['id']}-{hashlib.sha256(snap.read_bytes()).hexdigest()[:12]}"
        if not (built / "frechenlehen.glb").exists():
            cache.mkdir(parents=True, exist_ok=True)
            _export(snap, built)
            exported += 1
        target = public / "v" / v["id"]
        if not _same(built, target):                     # dev: every saved code/*.py runs this
            shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(built, target)
    public.mkdir(parents=True, exist_ok=True)
    (public / "versionen.json").write_text(json.dumps(list(reversed(listed)), ensure_ascii=False) + "\n",
                                           encoding="utf-8")
    return exported


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "freeze":
        vid = a[a.index("--id") + 1] if "--id" in a else datetime.date.today().isoformat()
        print(f"frozen: {freeze(ROOT, a[1], vid)}")
    elif len(a) == 2 and a[0] == "build":
        n = build(ROOT, a[1], ROOT / "tmp" / "versionen")
        print(f"versions: {len(load(ROOT))} in {a[1]}/v ({n} exported)")
    else:
        sys.exit(__doc__.strip().splitlines()[-1])
