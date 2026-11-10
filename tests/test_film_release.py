"""code/film_release.py: which films to delete, the encoder's bitrate, and purging old film blobs
from the git history (run on a throw-away repository)."""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
import film_release  # noqa: E402


def test_keeps_the_newest_two_films():
    names = ["2026-11-05_frechen_rundgang_threejs.mp4", "2026-11-08_frechen_rundgang_threejs.mp4",
             "2026-11-06_frechen_rundgang_threejs.mp4", "README.md", "frechenlehen_rundgang.mp4",
             "2026-11-07_frechen_rundgang_blender.mp4"]
    assert film_release.to_delete(names) == ["2026-11-05_frechen_rundgang_threejs.mp4"]
    assert film_release.to_delete(names[:2]) == []


def test_latest_is_the_newest_film():                                    # Pages serves it as rundgang.mp4
    names = ["2026-11-08_frechen_rundgang_threejs.mp4", "2026-11-09_frechen_rundgang_threejs.mp4",
             "2026-11-10_frechen_rundgang_blender.mp4", "README.md"]
    assert film_release.latest(names) == "2026-11-09_frechen_rundgang_threejs.mp4"


def test_bitrate_fits_the_target_size():
    kbps = film_release.video_kbps(305.28)
    size_mb = kbps * 1000 / 8 * 305.28 / 1e6
    assert 85 < size_mb < film_release.TARGET_MB < 100                       # GitHub rejects > 100 MB


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def test_purge_drops_every_film_blob_not_in_head(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com"); _git(repo, "config", "user.name", "t")
    commits = [{"a.mp4": "old a", "code.py": "1"},                            # a later deleted
               {"a.mp4": "old a", "b.mp4": "b v1", "code.py": "2"},
               {"b.mp4": "b v2", "c.mp4": "c", "code.py": "3"}]               # b overwritten
    for files in commits:
        for f in repo.glob("*"):
            if f.name != ".git":
                f.unlink()
        for name, text in files.items():
            (repo / name).write_text(text)
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "c")
    film_release.purge_history(repo, "main")
    blobs = {_git(repo, "cat-file", "-p", sha).strip() for sha in
             _git(repo, "rev-list", "--objects", "--all").split() if len(sha) == 40
             and _git(repo, "cat-file", "-t", sha).strip() == "blob"}
    assert {"b v2", "c", "1", "2", "3"} <= blobs                               # HEAD's films and all code
    assert not {"old a", "b v1"} & blobs                                       # old films gone
    assert (repo / "b.mp4").read_text() == "b v2" and _git(repo, "status", "--porcelain") == ""
    assert len(_git(repo, "log", "--oneline").splitlines()) == 3
