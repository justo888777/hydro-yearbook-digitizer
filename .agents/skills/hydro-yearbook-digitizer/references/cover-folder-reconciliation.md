# Cover and folder reconciliation

Folder names are hints, not authoritative metadata. The agent must identify the volume from the cover before processing the tables.

## Workflow

1. Find likely cover images among the first source files, using title-like layout and low table-line density.
2. Read cover fields in two independent passes.
3. Compare recognized basin and year with folder names and manifest values.
4. Produce one of:
   - `resolved`: cover and folder agree;
   - `needs_review`: conflict, ambiguity, or low image quality;
   - `verified`: human confirmed the canonical identity.
5. Suggest a canonical folder path, but never rename the source folder without explicit approval.

## Audit fields

Preserve:

- original folder path;
- cover source image;
- raw text and normalized cover fields;
- recognition candidates;
- conflicts;
- suggested canonical path;
- final approved identity.
