#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# ============================================================
# OpenRoot USB Backup v1  (backup_openroot_usb_v1.sh)
# Cold, verified, idempotent backup of the openroot repo to USB.
#
# Usage (on the OptiPlex):
#   bash bin/backup_openroot_usb_v1.sh                     # auto-find USB
#   bash bin/backup_openroot_usb_v1.sh --dev /dev/sdb1     # explicit partition
#   bash bin/backup_openroot_usb_v1.sh --models            # also copy ollama blobs (BIG)
#   bash bin/backup_openroot_usb_v1.sh --tag mybackup      # custom dir suffix
#
# What it does:
#   1. finds + mounts the first removable disk (or --dev)
#   2. rsync the whole repo (including .git -> the receipt chain history)
#   3. consistent snapshot of every sqlite db via VACUUM INTO (survives mid-write)
#   4. writes backup_info.json + sha256 manifest + verifies it
#   5. default: writes ollama `list` manifest only (re-pull is cheap);
#      pass --models to copy model blobs
# ============================================================
set -euo pipefail

REPO="${OPENROOT_REPO:-/home/jesse/openroot}"
DEV=""; COPY_MODELS=0; TAG="$(date +%Y%m%d_%H%M%S)"

while [ $# -gt 0 ]; do
  case "$1" in
    --dev)    DEV="$2"; shift 2 ;;
    --models) COPY_MODELS=1; shift ;;
    --tag)    TAG="$2"; shift 2 ;;
    *) echo "[held] unknown arg: $1"; exit 1 ;;
  esac
done

log(){ echo "[gate] $*"; }
ok(){  echo "[banked] $*"; }
die(){ echo "[held] $*"; exit 1; }

[ -d "$REPO" ] || die "repo not found: $REPO"

# ---- 1. locate USB device -----------------------------------
if [ -z "$DEV" ]; then
  log "scanning for removable disks..."
  DEV="$(lsblk -dnpo NAME,RM,SIZE,TYPE | awk '$2=="1" && $4=="disk"{print $1; exit}')"
  [ -n "$DEV" ] || die "no removable disk found. Plug the USB stick or pass --dev /dev/sdX"
fi
ok "target device: $DEV ($(lsblk -dno SIZE "$DEV"))"

# ---- 2. pick first partition + mount ------------------------
PART="$(lsblk -nrpo NAME,TYPE "$DEV" | awk '$2=="part"{print $1; exit}')"
PART="${PART:-$DEV}"
MNT="$(lsblk -nrno MOUNTPOINT "$PART" | head -1 || true)"

if [ -z "$MNT" ]; then
  log "mounting $PART ..."
  if command -v udisksctl >/dev/null 2>&1; then
    if udisksctl mount -b "$PART" --no-user-interaction; then
      MNT="$(lsblk -dnro MOUNTPOINT "$PART" | head -1 || true)"
    fi
  fi

  if [ -z "$MNT" ]; then
    run_mount_privileged() {
      if [ "$(id -u)" -eq 0 ]; then
        "$@"
      elif command -v sudo >/dev/null 2>&1; then
        sudo "$@"
      else
        die "mounting requires root or sudo"
      fi
    }

    mount_dir=/mnt/openroot_usb
    run_mount_privileged mkdir -p "$mount_dir"

    if mountpoint -q "$mount_dir"; then
      die "$mount_dir is already mounted; inspect it before proceeding"
    fi

    fs_type="$(lsblk -dnro FSTYPE "$PART")"
    owner_uid="${SUDO_UID:-$(id -u)}"
    owner_gid="${SUDO_GID:-$(id -g)}"

    case "$fs_type" in
      vfat|exfat)
        run_mount_privileged mount           -o "uid=$owner_uid,gid=$owner_gid,umask=077"           "$PART" "$mount_dir"
        ;;
      *)
        run_mount_privileged mount "$PART" "$mount_dir"
        ;;
    esac

    MNT="$(lsblk -dnro MOUNTPOINT "$PART" | head -1 || true)"
  fi
fi

[ -n "$MNT" ] || die "no mount point found for $PART"
mountpoint -q "$MNT" || die "not a mounted filesystem: $MNT"
[ -w "$MNT" ] || die "mount point is not writable by the invoking user: $MNT"
ok "mounted at: $MNT"

# ---- 3. space check -----------------------------------------
AVAIL_MB="$(df -Pm "$MNT" | awk 'NR==2{print $4}')"
NEED_MB="$(du -sm "$REPO" | awk '{print $1}')"
if [ "$AVAIL_MB" -le "$((NEED_MB + 256))" ]; then
  die "not enough space on USB: need ~${NEED_MB}MB (+headroom), have ${AVAIL_MB}MB"
fi
ok "space ok: need ~${NEED_MB}MB, have ${AVAIL_MB}MB"

DEST="$MNT/openroot_backup_$TAG"
mkdir -p "$DEST"

# ---- 4. rsync repo (FAT-safe flags, keep .git) ---------------
log "rsync repo -> $DEST/repo"
rsync -rlptD \
      --exclude='__pycache__' --exclude='.pytest_cache' \
      --info=stats1,progress2 \
      "$REPO/" "$DEST/repo/"
ok "repo copied"

# ---- 5. consistent sqlite snapshots -------------------------
log "safe-copy sqlite dbs (VACUUM INTO)"
mkdir -p "$DEST/dbs"
if command -v sqlite3 >/dev/null 2>&1; then
  n_dbs=0
  while IFS= read -r -d '' f; do
    rel="${f#"$REPO"/}"
    out="$DEST/dbs/$rel"
    mkdir -p "$(dirname "$out")"

    [ ! -e "$out" ] || die "snapshot already exists: $out"
    tmp="$(mktemp "$out.tmp.XXXXXX")"
    sql_tmp="$(printf '%s' "$tmp" | sed "s/'/''/g")"

    if sqlite3 -readonly "$f" "VACUUM INTO '$sql_tmp'"; then
      if integrity="$(sqlite3 -readonly "$tmp" 'PRAGMA integrity_check;')" &&
         [ "$integrity" = "ok" ]; then
        mv -- "$tmp" "$out"
        ok "sealed snapshot: $rel"
        n_dbs=$((n_dbs + 1))
      else
        rm -f -- "$tmp"
        die "snapshot integrity check failed: $rel"
      fi
    else
      rm -f -- "$tmp"
      die "consistent SQLite snapshot failed: $rel; backup incomplete"
    fi
  done < <(find "$REPO" -type f \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' \) -print0)

  if [ "$n_dbs" -gt 0 ]; then
    ok "$n_dbs consistent db snapshot(s) written"
  else
    log "no sqlite dbs found under repo"
  fi
else
  if [ "${OPENROOT_ALLOW_RAW_SQLITE:-0}" != "1" ]; then
    die "sqlite3 CLI missing: install it; raw fallback requires OPENROOT_ALLOW_RAW_SQLITE=1 and all database writers stopped"
  fi
  log "WARNING: raw SQLite fallback explicitly allowed by operator; all database writers must be stopped; database consistency is not verified"
fi

# ---- 6. ollama models: manifest by default, blobs optional ---
OMDIR="$HOME/.ollama/models"
[ -d "$OMDIR" ] || OMDIR="/usr/share/ollama/.ollama/models"
if [ "$COPY_MODELS" = "1" ]; then
  if [ -d "$OMDIR" ]; then
    log "copying ollama model blobs from $OMDIR (this can take a long time)"
    rsync -rlptD "$OMDIR/" "$DEST/ollama_models/"
    ok "ollama model blobs copied"
  else
    log "no ollama models dir found; skipping blob copy"
  fi
else
  if command -v ollama >/dev/null 2>&1; then
    ollama list > "$DEST/models_manifest.txt" 2>/dev/null || true
    ok "models manifest written (blobs NOT copied; re-pull reproduces them; use --models to copy)"
  fi
fi

# ---- 7. info + manifest + verify ----------------------------
GITSHA="$(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo 'not-a-git-repo')"
cat > "$DEST/backup_info.json" <<JSON
{
  "tool": "backup_openroot_usb_v1",
  "tag": "$TAG",
  "created": "$(date -Iseconds)",
  "repo": "$REPO",
  "git_head": "$GITSHA",
  "device": "$DEV",
  "mount": "$MNT"
}
JSON

log "writing sha256 manifest"
( cd "$DEST" && find . -type f ! -name MANIFEST.sha256 -print0 \
  | sort -z | xargs -0 sha256sum > MANIFEST.sha256 )

log "verifying manifest"
if ( cd "$DEST" && sha256sum -c --quiet MANIFEST.sha256 ); then
  ok "manifest verified: every file matches its hash"
else
  die "manifest verification FAILED - backup is not trustworthy"
fi

ok "backup size: $(du -sh "$DEST" | awk '{print $1}')"
ok "USB backup complete: $DEST"
echo "[exit=0]"
