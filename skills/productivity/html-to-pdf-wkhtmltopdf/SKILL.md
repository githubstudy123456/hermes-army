---
name: html-to-pdf-wkhtmltopdf
description: Convert HTML files to PDF using wkhtmltopdf CLI, with pdftk merge for batch operations. Alternative to WeasyPrint when it hangs.
category: productivity
---

# HTML to PDF Conversion (wkhtmltopdf)

Convert web pages / HTML files to PDF using `wkhtmltopdf` CLI tool.

## Prerequisites

```bash
# Install tools
sudo apt-get install -y wkhtmltopdf pdftk
```

## Quick Convert (Single File)

```bash
wkhtmltopdf --enable-local-file-access --orientation Portrait --page-size A4 \
    --margin-top 20 --margin-bottom 20 --margin-left 25 --margin-right 25 \
    input.html output.pdf
```

## Batch Convert (Multiple Files)

```bash
for i in $(seq -f "%02g" 1 25); do
    wkhtmltopdf --enable-local-file-access --orientation Portrait --page-size A4 \
        --margin-top 20 --margin-bottom 20 --margin-left 25 --margin-right 25 \
        --footer-center "第 ${i} 章" \
        chapter_${i}.htm capitalism_ch${i}.pdf
done
```

## Merge PDFs (pdftk)

```bash
pdftk file1.pdf file2.pdf file3.pdf cat output merged.pdf
```

## Known Issues

- **WeasyPrint hangs**: Do NOT use WeasyPrint for large HTML files — it blocks/times out
- **pandoc + wkhtmltopdf fails**: Direct wkhtmltopdf CLI works when pandoc pipeline fails
- **Python PDF libs (fpdf2, reportlab, xhtml2pdf)**: Often not installed and pip mirrors may fail — use wkhtmltopdf directly instead
- `--enable-local-file-access` flag is required when converting local HTML files with relative CSS/image links

## Example: marxoists.org Chinese Book to PDF

```bash
BASE_URL="https://www.marxists.org/chinese/marx/capital"
mkdir -p ~/download/file

# Download chapters (e.g. 01-25)
for i in $(seq 1 25); do
    curl -sL -A "Mozilla/5.0" -o chapter_$(printf %02d $i).htm \
        "$BASE_URL/$(printf %02d $i).htm"
done

# Convert each chapter
for i in $(seq -f "%02g" 1 25); do
    wkhtmltopdf --enable-local-file-access --page-size A4 \
        --margin-top 20 --margin-bottom 20 \
        chapter_${i}.htm capitalism_ch${i}.pdf
done

# Merge all into one PDF
pdftk capitalism_ch*.pdf cat output 资本论_第一卷_完整版.pdf
```
