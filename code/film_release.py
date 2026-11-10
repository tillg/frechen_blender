"""Frechenlehen – releasing the Rundgang film (used by `just film`, pure Python + git, no bpy).

- to_delete(names): the films (YYYY-MM-DD_frechen_rundgang_threejs.mp4) older than the newest two.
- latest(names): the newest film (GitHub Pages serves it as rundgang.mp4, see pages.yml).
- video_kbps(seconds): the H.264 bitrate for a two-pass encode that ends near TARGET_MB, safely
  under GitHub's 100 MB file limit, whatever the film's length (25 fps stays).
- purge_history(repo, branch): rewrites branch so that no commit holds a .mp4 blob other than the
  ones in its tip, then drops the old objects locally (refs/original, reflog, gc). Pushing the
  rewritten branch (force) is the caller's job.

CLI:  film_release.py kbps <frames>  |  prune <dir>  |  latest <dir>  |  purge <branch>  |  index-filter (internal)
"""
import os, re, subprocess, sys
from pathlib import Path

FILM = re.compile(r"^(\d{4}-\d{2}-\d{2})_frechen_rundgang_threejs\.mp4$")
KEEP, FPS, TARGET_MB = 2, 25, 90


def to_delete(names, keep=KEEP):
    """Film file names to delete: all but the newest `keep` by the date in the name."""
    films = sorted((n for n in names if FILM.match(n)), reverse=True)
    return sorted(films[keep:])


def latest(names):
    """The newest film's file name, by the date in the name."""
    return max(n for n in names if FILM.match(n))


def video_kbps(seconds, target_mb=TARGET_MB):
    """Video bitrate in kbit/s so that the file ends near target_mb (2 % for the container)."""
    return int(target_mb * 1e6 * 8 * 0.98 / seconds / 1000)


def _git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          env=env).stdout


def _film_blobs(repo, rev):
    return {line.split()[2] for line in _git(repo, "ls-tree", "-r", rev).splitlines()
            if line.split("\t")[-1].endswith(".mp4")}


def purge_history(repo, branch):
    """Rewrite `branch` so only the .mp4 blobs of its tip remain anywhere in its history."""
    keep = _film_blobs(repo, branch)
    old = {sha for rev in _git(repo, "rev-list", branch).split() for sha in _film_blobs(repo, rev)} - keep
    if old:
        env = dict(os.environ, FILTER_BRANCH_SQUELCH_WARNING="1", KEEP_BLOBS=" ".join(sorted(keep)))
        filt = f"{sys.executable} {Path(__file__).resolve()} index-filter"
        _git(repo, "filter-branch", "-f", "--index-filter", filt, "--", branch, env=env)
        for ref in _git(repo, "for-each-ref", "--format=%(refname)", "refs/original/").split():
            _git(repo, "update-ref", "-d", ref)
    _git(repo, "reflog", "expire", "--expire=now", "--all")
    _git(repo, "gc", "-q", "--prune=now")
    return len(old)


def _index_filter():
    """Inside filter-branch: unstage every .mp4 whose blob is not one of KEEP_BLOBS."""
    keep = set(os.environ.get("KEEP_BLOBS", "").split())
    drop = [line.split("\t", 1)[1] for line in _git(".", "ls-files", "-s").splitlines()
            if line.endswith(".mp4") and line.split()[1] not in keep]
    if drop:
        _git(".", "rm", "--cached", "-q", "--ignore-unmatch", "--", *drop)


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    if cmd == "kbps":
        print(video_kbps(int(rest[0]) / FPS))
    elif cmd == "prune":
        print("\n".join(to_delete(os.listdir(rest[0]))))
    elif cmd == "latest":
        print(latest(os.listdir(rest[0])))
    elif cmd == "purge":
        print(f"{purge_history('.', rest[0])} old film blob(s) removed from {rest[0]}")
    elif cmd == "index-filter":
        _index_filter()
    else:
        sys.exit(__doc__)
