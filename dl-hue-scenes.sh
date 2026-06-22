#!/bin/bash
# Téléchargement des images hue-scenes depuis GitHub
# À exécuter dans LXC03 : pct exec 210 -- bash /tmp/dl-hue-scenes.sh

REPO="https://raw.githubusercontent.com/theroyaldave/proxmox/main/hue-scenes"
DEST="/var/www/snapcast-ui/hue-scenes"

mkdir -p "$DEST"

FILES=(
  "Aurore_boreale.jpg"
  "Chinatown.jpg"
  "Concentration.jpg"
  "Coucher_de_soleil.jpg"
  "Detente.jpg"
  "Eclosion_ambree.jpg"
  "Honolulu.jpg"
  "Ibiza.jpg"
  "Lecture.jpg"
  "Lumineux.jpg"
  "Magneto.jpg"
  "Malibu_pink.jpg"
  "Miami.jpg"
  "Rio.jpg"
  "Rouge_gorge.jpg"
  "Soho.jpg"
  "Sommeil.jpg"
  "Starlight.jpg"
  "Tokyo.jpg"
  "Veilleuse.jpg"
  "Ville_de_lamour.jpg"
)

for f in "${FILES[@]}"; do
  echo -n "Téléchargement $f... "
  wget -q "$REPO/$f" -O "$DEST/$f" && echo "OK" || echo "ERREUR"
done

echo ""
echo "Fichiers dans $DEST :"
ls -lh "$DEST"
