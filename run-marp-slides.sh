#!/bin/sh
for file in presentation/*.md; do
  name=$(basename "$file" .md)
  echo "Building: $file"
  marp "$file" --pdf --allow-local-files --output "tmp/presentation/dist/$name.pdf"
  marp "$file" --pptx --allow-local-files --output "tmp/presentation/dist/$name.pptx"
done
