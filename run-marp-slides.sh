#!/bin/sh
mkdir -p tmp/presentation/dist
chmod -R a+rwx tmp/presentation

for file in presentation/*.md; do
  name=$(basename "$file" .md)
  echo "Building $file -> $name.[pdf|pptx]"

  docker run --rm --init \
    -v "$PWD/presentation:/home/marp/app/" \
    -v "$PWD/tmp/presentation/dist:/home/marp/output/" \
    -e LANG=$LANG \
    marpteam/marp-cli \
    "$(basename "$file")" \
    --pdf --allow-local-files \
    --output "/home/marp/output/$name.pdf"

  docker run --rm --init \
    -v "$PWD/presentation:/home/marp/app/" \
    -v "$PWD/tmp/presentation/dist:/home/marp/output/" \
    -e LANG=$LANG \
    marpteam/marp-cli \
    "$(basename "$file")" \
    --pptx --allow-local-files \
    --output "/home/marp/output/$name.pptx"
done
