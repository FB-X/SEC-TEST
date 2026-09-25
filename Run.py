import os
import sys
import shutil
import hashlib
import importlib.util
import subprocess

TERMUX_PREFIX = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
PYVER = f"python{sys.version_info.major}.{sys.version_info.minor}"
SITE_PACKAGES = f"{TERMUX_PREFIX}/lib/{PYVER}/site-packages"
ALIREQ_DIR = f"{SITE_PACKAGES}/alireq"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_REQUESTS = os.path.join(HERE, "requests")

SO_FILES = [
    "alireq.cpython-314-aarch64-linux-android.so",
    "android_shield.cpython-314-aarch64-linux-android.so",
    "api.cpython-314-aarch64-linux-android.so",
    "exceptions.cpython-314-aarch64-linux-android.so",
    "libandroid_shield.so",
    "models.cpython-314-aarch64-linux-android.so",
    "sessions.cpython-314-aarch64-linux-android.so",
]

EXTRA_FILES = [
    "__init__.py",
]

FBXXX_SO = "FBXXX.cpython-314-aarch64-linux-android.so"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def step(msg):
    print(f"[*] {msg}")


def fail(msg):
    print(f"[!] {msg}")
    sys.exit(1)


def remove_old_alireq():
    step(f"Removing old alireq runtime at {ALIREQ_DIR}")
    if os.path.isdir(ALIREQ_DIR):
        shutil.rmtree(ALIREQ_DIR)
    if os.path.isdir(SITE_PACKAGES):
        for name in os.listdir(SITE_PACKAGES):
            if name.startswith("alireq") or name.startswith("android_shield"):
                p = os.path.join(SITE_PACKAGES, name)
                try:
                    if os.path.isdir(p):
                        shutil.rmtree(p)
                    else:
                        os.remove(p)
                except Exception:
                    pass


def make_alireq_dir():
    step(f"Creating {ALIREQ_DIR}")
    os.makedirs(ALIREQ_DIR, exist_ok=True)


def copy_file(src, dst):
    if not os.path.isfile(src):
        fail(f"Missing source: {src}")
    shutil.copyfile(src, dst)
    if dst.endswith(".so"):
        os.chmod(dst, 0o700)
    return sha256_of(src), sha256_of(dst)


def copy_all():
    step("Copying .so files and __init__.py into alireq package")
    for name in SO_FILES + EXTRA_FILES:
        src = os.path.join(REPO_REQUESTS, name)
        dst = os.path.join(ALIREQ_DIR, name)
        s_src, s_dst = copy_file(src, dst)
        if s_src != s_dst:
            fail(f"Hash mismatch after copy: {name}")
        print(f"    [ok] {name}")


def copy_FBXXX_so():
    step("Copying FBXXX.so into alireq package")
    src = os.path.join(HERE, FBXXX_SO)
    dst = os.path.join(ALIREQ_DIR, FBXXX_SO)
    s_src, s_dst = copy_file(src, dst)
    if s_src != s_dst:
        fail("FBXXX.so hash mismatch after copy")
    print(f"    [ok] {FBXXX_SO}")


def verify_layout():
    step("Verifying installed layout")
    expected = SO_FILES + EXTRA_FILES + [FBXXX_SO]
    missing = []
    for name in expected:
        p = os.path.join(ALIREQ_DIR, name)
        if not os.path.isfile(p):
            missing.append(name)
    if missing:
        fail(f"Missing after install: {missing}")
    for name in SO_FILES:
        src = os.path.join(REPO_REQUESTS, name)
        dst = os.path.join(ALIREQ_DIR, name)
        if sha256_of(src) != sha256_of(dst):
            fail(f"Hash mismatch for {name}")
    print("    [ok] all files present and hashes match")


def add_alireq_to_path():
    if ALIREQ_DIR not in sys.path:
        sys.path.insert(0, ALIREQ_DIR)


def check_native_shield():
    step("Checking native shield")
    lib_path = os.path.join(ALIREQ_DIR, "libandroid_shield.so")
    if not os.path.isfile(lib_path):
        fail("libandroid_shield.so not present")
    import ctypes
    try:
        lib = ctypes.CDLL(lib_path)
    except OSError as e:
        fail(f"Failed to load native shield: {e}")
    try:
        abi = int(lib.shield_abi_version())
    except AttributeError:
        fail("native shield missing shield_abi_version")
    if abi != 4:
        fail(f"Native shield ABI mismatch: got {abi}, expected 4")
    print(f"    [ok] native shield ABI={abi}")


def check_pycryptodome():
    step("Checking pycryptodome")
    try:
        __import__("Crypto.Hash.keccak")
        print("    [ok] pycryptodome present")
    except Exception:
        print("    [*] installing pycryptodome")
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "pycryptodome"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if r.returncode != 0:
            fail("pycryptodome install failed")
        print("    [ok] pycryptodome installed")


def check_ld_library_path():
    prefix_lib = f"{TERMUX_PREFIX}/lib"
    cur = os.environ.get("LD_LIBRARY_PATH", "")
    parts = [p for p in cur.split(":") if p]
    if prefix_lib not in parts:
        parts.insert(0, prefix_lib)
        os.environ["LD_LIBRARY_PATH"] = ":".join(parts)
        print(f"    [ok] LD_LIBRARY_PATH updated: {os.environ['LD_LIBRARY_PATH']}")
    else:
        print(f"    [ok] LD_LIBRARY_PATH already contains {prefix_lib}")


def load_FBXXX():
    step("Loading FBXXX.so")
    path = os.path.join(ALIREQ_DIR, FBXXX_SO)
    if not os.path.isfile(path):
        fail(f"FBXXX.so not found at {path}")
    spec = importlib.util.spec_from_file_location("FBXXX", path)
    if spec is None or spec.loader is None:
        fail("Failed to build spec for FBXXX.so")
    module = importlib.util.module_from_spec(spec)
    sys.modules["FBXXX"] = module
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        fail(f"Failed to load FBXXX.so: {e}")
    if not hasattr(module, "main"):
        fail("FBXXX.so has no main() function")
    print("    [ok] FBXXX.so loaded")
    return module


def main():
    print("[*] AliReq client runner")
    print(f"[*] HOME = {HERE}")
    print(f"[*] TARGET = {ALIREQ_DIR}")

    remove_old_alireq()
    make_alireq_dir()
    copy_all()
    copy_FBXXX_so()
    verify_layout()
    add_alireq_to_path()
    check_ld_library_path()
    check_pycryptodome()
    check_native_shield()
    FBXXX = load_FBXXX()
    step("Launching FBXXX.main()")
    FBXXX.main()


if __name__ == "__main__":
    main()
