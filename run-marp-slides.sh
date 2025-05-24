#!/bin/sh
for file in presentation/*.md; do
  name=$(basename "$file" .md)
  marp "$file" --pdf --allow-local-files --output "presentation/dist/$name.pdf"
  marp "$file" --pptx --allow-local-files --output "presentation/dist/$name.pptx"
done
