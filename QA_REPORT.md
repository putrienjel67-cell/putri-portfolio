# Portfolio Recruiter Redesign QA Report

## Test environment

- Branch: `portfolio-recruiter-redesign`
- Local server: Python static HTTP server
- Browser: installed Google Chrome controlled with Playwright
- Viewports: 360, 390, 430, 768, 1024, and 1440 pixels
- Automated browser result: 108 passed, 108 total, 0 failed, 0 console errors

## Project coverage

Each of the ten projects was opened directly through its hash route, refreshed, and checked for content, screenshot loading, workbook responses, and lightbox behavior.

- [x] PROJ-001 Product Catalog Cleanup
- [x] PROJ-002 Customer Data Cleanup
- [x] PROJ-003 Order Reconciliation
- [x] PROJ-004 Invoice Validation and VA Workflow
- [x] PROJ-005 Inventory Audit
- [x] PROJ-006 Employee Records Control
- [x] PROJ-007 Shipping Control
- [x] PROJ-008 Transaction Reconciliation
- [x] PROJ-009 Healthcare Records Control
- [x] PROJ-010 Multi-Source Data Merge

## Required QA checklist

- [x] All 10 projects accessible from All Projects
- [x] All 3 Selected Work projects accessible
- [x] All 108 intended screenshots load in Chrome
- [x] Two unreferenced duplicate evidence files remain preserved but are not displayed
- [x] All 17 workbook links return successful local HTTP responses
- [x] External Python repository URL verified with HTTP 200
- [x] Existing LinkedIn URL preserved
- [x] Existing Upwork URL preserved
- [x] Existing Fiverr short link verified with HTTP 200
- [x] Email uses `mailto:putrienjel67@gmail.com`
- [x] Mobile navigation opens and closes correctly
- [x] Native project links open with keyboard Enter
- [x] Case-study dialog controls use native buttons
- [x] Lightbox opens, closes with Escape, and supports previous and next controls
- [x] Lightbox returns focus to the triggering screenshot
- [x] Direct project loading works
- [x] Project refresh works
- [x] Browser back closes the project and returns to the page
- [x] No horizontal overflow at all six required viewport widths
- [x] No horizontal overflow in case study at 390 and 1440 pixels
- [x] No browser console errors
- [x] No missing referenced assets
- [x] No invented clients, testimonials, certifications, employers, revenue, or business impact
- [x] Practice-project disclosure remains visible and accurate
- [x] Static file architecture remains compatible with GitHub Pages

## Accessibility review

- [x] One H1 on the homepage
- [x] Section headings use ordered semantic levels
- [x] Native anchors and buttons replace fake clickable cards
- [x] Skip link provided
- [x] Visible focus outline provided
- [x] Mobile menu exposes `aria-expanded` and `aria-controls`
- [x] Dialogs have accessible labels
- [x] Evidence buttons include descriptive labels and image alt text
- [x] Decorative project thumbnails use empty alt text
- [x] Live regions announce case-study and lightbox state changes
- [x] Reduced-motion preference disables transitions and smooth scrolling
- [x] Text and controls use high-contrast ink, green, and warm neutral tokens

## Performance review

- Hero image has explicit dimensions and high fetch priority
- Selected Work evidence loads eagerly because it is the primary proof
- All Project thumbnails, About photo, and gallery screenshots use lazy loading
- Images reserve layout space with width, height, and aspect ratio
- No framework or animation library was added
- JavaScript remains limited to rendering, routing, dialogs, gallery controls, and mobile navigation
- Image failure state is visible and does not leave a broken control

## Bugs found and fixed

1. The generated Selected Work path used `p003.png` instead of the existing `p03.png`. The preview path now uses the repository naming convention.
2. The previous card implementation used `role="link"` on articles. Project entries now use native anchors.
3. The previous lightbox lacked image navigation, a visible caption, and complete focus return. All three were added.
4. Case-study evidence had no clear Input, Process, and Output sequence. Screenshots are now grouped by workflow role without inventing new evidence.
5. The username-based Fiverr URL returned 404. The existing verified short link from `main` was preserved instead.

## Preserved but unused files

No evidence was deleted. The following items remain available in the branch even though the redesigned interface does not load them:

- `assets/projects/proj-001/EV-09_Records_Requiring_Action.png`
- `assets/projects/proj-003/EV-07C_Shipped_No_Dispatch_Row_5.png`
- older portrait and cutout variants identified in `AUDIT.md`

## Preview instructions

From the repository folder:

```powershell
python -m http.server 4180
```

Then open:

`http://localhost:4180/`

Direct route example:

`http://localhost:4180/#case-proj-003`

The redesign remains isolated from `main` until the branch is reviewed and explicitly merged.
