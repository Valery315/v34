import os
import shutil
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent.parent
PERSISTENT_ENV_VARS = (
    "DATA_DIR",
    "RAILWAY_VOLUME_PATH",
    "RAILWAY_VOLUME_MOUNT_PATH",
    "STORAGE_DIR",
    "PERSISTENT_DIR",
)
PERSISTENT_PATH_CANDIDATES = (
    "/data",
    "/mnt/data",
    "/volume",
    "/persistent",
    "/storage",
)
MUTABLE_PATHS = (
    "database/Player",
    "database/Club",
    "database/leaders.db",
    "JSON",
    "users.db",
)


def _resolve_persistent_root():
    for env_name in PERSISTENT_ENV_VARS:
        value = os.getenv(env_name)
        if value:
            return Path(value).expanduser()

    for candidate in PERSISTENT_PATH_CANDIDATES:
        path = Path(candidate)
        if path.exists() and path.is_dir():
            return path

    return None


def _seed_if_missing(source: Path, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        return

    if source.exists():
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)
        return

    if source.suffix:
        target.touch()
    else:
        target.mkdir(parents=True, exist_ok=True)


def _replace_with_symlink(source: Path, target: Path):
    if source.is_symlink():
        if source.resolve() == target.resolve():
            return
        source.unlink()
    elif source.exists():
        if source.is_dir():
            shutil.rmtree(source)
        else:
            source.unlink()

    source.parent.mkdir(parents=True, exist_ok=True)
    source.symlink_to(target, target_is_directory=target.is_dir())


def bootstrap_persistent_storage():
    persistent_root = _resolve_persistent_root()
    if persistent_root is None:
        print("[ИНФО] Persistent storage не настроен, используется локальный /app.")
        return None

    persistent_root.mkdir(parents=True, exist_ok=True)
    state_root = persistent_root / "speedbrawl_state"
    state_root.mkdir(parents=True, exist_ok=True)

    for relative_path in MUTABLE_PATHS:
        source = APP_ROOT / relative_path
        target = state_root / relative_path
        _seed_if_missing(source, target)
        _replace_with_symlink(source, target)

    print(f"[ИНФО] Persistent storage подключен: {state_root}")
    return state_root
