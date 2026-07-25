#!/bin/zsh
set -euo pipefail

preview_root="$(cd "$(dirname "$0")/.." && pwd)"
preview_port="8765"
preview_origin="http://127.0.0.1:${preview_port}"
preview_url="${preview_origin}/super_frgmnts.html?preview=foundry-expansion&minion=1"

if curl --silent --fail --max-time 1 "${preview_origin}/super_frgmnts.html" >/dev/null 2>&1; then
    open "${preview_url}"
    exit 0
fi

cd "${preview_root}"
python3 -m http.server "${preview_port}" --bind 127.0.0.1 &
preview_server_pid=$!

cleanup_preview_server() {
    if kill -0 "${preview_server_pid}" >/dev/null 2>&1; then
        kill "${preview_server_pid}"
    fi
}

trap cleanup_preview_server EXIT INT TERM

sleep 0.5
open "${preview_url}"

echo
echo "SUPER FRGMNTS local preview is running:"
echo "${preview_url}"
echo
echo "Keep this window open while you play."
echo "Press Control-C here when you are finished."
echo

wait "${preview_server_pid}"
