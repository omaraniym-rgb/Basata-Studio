#!/bin/bash
# usage: run2.sh LOG OUTDIR W H DPR names...  (keeps the local server alive, resumable)
cd "$(dirname "$0")"; LOG=$1; shift
curl -s -m 2 -o /dev/null http://127.0.0.1:8765/lib3d2.html || (setsid nohup python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &); sleep 1
python3 r3d2.py "$@" >> "$LOG" 2>&1
