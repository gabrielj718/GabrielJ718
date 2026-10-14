"""Shared bits for the tests: run a script the way the skill does, make scratch dirs, synthesise media.
Paths are relative to this file (SCRIPTS = the folder above tests/), so the tests run from any install location."""
import json, os, shutil, subprocess, sys, tempfile, unittest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
needs_ffmpeg = unittest.skipUnless(HAS_FFMPEG, "ffmpeg / ffprobe not on PATH")


def run(script, *args):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + [str(a) for a in args], capture_output=True, text=True)


def scratch(test):
    d = tempfile.mkdtemp(prefix="yt-edit-test-")
    test.addCleanup(shutil.rmtree, d, True)
    return d


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text if isinstance(text, str) else json.dumps(text))
    return path


def read(path):
    with open(path) as f:
        return f.read()


def load(path):
    return json.loads(read(path))


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + list(args), check=True)


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-show_entries", "format=duration",
                        "-of", "json", path], capture_output=True, text=True, check=True)
    p = json.loads(r.stdout)
    return {s["codec_type"]: float(s["duration"]) for s in p["streams"]}, float(p["format"]["duration"])
