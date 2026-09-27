#!/data/data/com.termux/files/usr/bin/bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DST="$HOME/ALI_CLIENT"
mkdir -p "$DST"
cp -rv "$SRC"/* "$DST/"
echo "[OK] Installed to $DST"
echo "Run: cd $DST && python3 Run.py"
