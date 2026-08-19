# Photo-to-PDF policy

## Purpose

A PDF is useful as a compact browsing, ordering, and sharing container. One two-page photograph becomes one PDF page unless pages are split first.

## Important limitation

Converting JPEG photographs to PDF does not inherently improve OCR and does not inherently reduce processing cost. A PDF can simply embed the same images. Downsampling or stronger JPEG compression makes the file smaller but may erase decimal points and thin digits.

Therefore:

1. keep original photos immutable;
2. create an optional derived `source_browse.pdf` for convenient viewing;
3. perform OCR from original photos or rectified page/table images;
4. do not use the compressed PDF as the only source of truth;
5. verify page count and visual legibility after PDF generation.

Use `hydro-yearbook photos-to-pdf` only for the derived browsing PDF. The default workflow should not delete or replace photographs.
