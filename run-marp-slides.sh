#!/bin/sh
mkdir -p tmp/presentation/dist
chmod -R a+rwx tmp/presentation

for file in presentation/*.md; do
  name=$(basename "$file" .md)
  echo "Building $file -> $name.[pdf|pptx]"

  docker run --rm --init \
    -v "$PWD:/home/marp/app/" \
    -e LANG=$LANG \
    marpteam/marp-cli \
    "$file" --pdf --allow-local-files --output "tmp/presentation/dist/$name.pdf"

  docker run --rm --init \
    -v "$PWD:/home/marp/app/" \
    -e LANG=$LANG \
    marpteam/marp-cli \
    "$file" --pptx --allow-local-files --output "tmp/presentation/dist/$name.pptx"
done
