#!/bin/bash
set -e
cd /home/claude/vsc
python3 - <<'P'
s=open('scene.html').read();h=open('hcss.txt').read();open('scene-h.html','w').write(s.replace("<!--HCSS-->",h))
P
