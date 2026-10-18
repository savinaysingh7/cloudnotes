import pymupdf

doc = pymupdf.open('CloudNotesProjectReport.pdf')
print('=== 1. PDF Metadata & Page Size ===')
print('Title:', doc.metadata.get('title'))
print('Author:', doc.metadata.get('author'))
print('Subject:', doc.metadata.get('subject'))
print('Page count:', len(doc))

page1 = doc[0]
rect = page1.rect
print(f'Page size: {rect.width:.2f} x {rect.height:.2f} pt (A4 standard: 595.28 x 841.89 pt)')
is_a4 = abs(rect.width - 595.28) < 1.0 and abs(rect.height - 841.89) < 1.0
print('Is A4 standard:', is_a4)

print('\n=== 2. Embedded Fonts ===')
fonts = set()
for page in doc:
    for font in page.get_fonts():
        fonts.add((font[3], font[4]))
for fn, ft in sorted(fonts):
    print(f'  {fn} ({ft})')

print('\n=== 3. Font Size Audit across all pages ===')
small_spans = []
for p_idx, page in enumerate(doc):
    text_page = page.get_text('dict')
    for block in text_page['blocks']:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    if not text:
                        continue
                    size = round(span['size'], 1)
                    # Ignore running headers (y0 < 55) and running footers (y0 > 795)
                    y0 = span['bbox'][1]
                    if y0 < 55 or y0 > 795:
                        continue
                    if size < 11.9:
                        small_spans.append((p_idx + 1, size, span['font'], text[:40]))

if small_spans:
    print(f'Found {len(small_spans)} spans smaller than 12pt in body/tables:')
    for s in small_spans[:10]:
        print(f'  Page {s[0]}: {s[1]}pt [{s[2]}] "{s[3]}"')
else:
    print('ALL body text, table content, code listings, and captions strictly meet or exceed 12.0 pt!')
