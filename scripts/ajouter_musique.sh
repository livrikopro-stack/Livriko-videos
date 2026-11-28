#!/usr/bin/env bash
# Ajoute une musique de musiques/ à une vidéo (sans toucher à l'image).
# Usage : bash scripts/ajouter_musique.sh video_sans_son.mp4 musiques/NN-xxx.mp3 DUREE_S sortie.mp4
# - musique douce mais audible (normalisée à -24 LUFS, la même force pour toutes les musiques)
# - commence au début du morceau, fondu d'entrée 0,3 s, fondu de sortie 1 s, coupée à DUREE_S
# - choisir un morceau au moins aussi long que la vidéo (voir musiques/musiques.csv)
set -euo pipefail
VID="$1"; MUS="$2"; DUR="$3"; OUT="$4"
FO=$(python3 -c "print(max(0.0, float('$DUR') - 1.0))")
ffmpeg -v error -y -i "$VID" -i "$MUS" \
  -filter_complex "[1:a]atrim=0:${DUR},asetpts=PTS-STARTPTS,loudnorm=I=-24:TP=-2:LRA=11,aresample=44100,afade=t=in:st=0:d=0.3,afade=t=out:st=${FO}:d=1[a]" \
  -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 160k -ac 2 -t "$DUR" -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration:stream=codec_name -of compact "$OUT"
