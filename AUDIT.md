# Recruiter Portfolio Audit

## Scope and safety

- Audited latest `origin/main` at commit `69ccb12`.
- Work is isolated on `portfolio-recruiter-redesign`.
- The live `main` branch remains unchanged.
- The original 10 practice projects remain the primary portfolio collection.

## Current architecture

- Static GitHub Pages site using `index.html`, `project-data.js`, and `case-studies.js`.
- Ten project summaries are hard-coded in the homepage, while detailed case-study content is data-driven from `project-data.js`.
- Case studies open in a native `dialog` and use URL hashes such as `#case-proj-003`.
- Galleries and workbook downloads are rendered dynamically.
- No heavy framework or runtime dependency is present.

## Asset inventory

- 110 PNG files exist inside project evidence folders.
- 108 screenshots are referenced by the ten case studies.
- 17 Excel workbooks exist and all referenced download paths resolve.
- 10 homepage preview images duplicate the corresponding project dashboard image by design.
- Two evidence files exist but are not referenced: `PROJ-001/EV-09` and `PROJ-003/EV-07C`.
- Five older portrait or cutout variants are currently unused.
- No referenced image or workbook path is missing.

## What already works

- Every project has truthful summary, scope, workflow, tools, result, skills, evidence, and downloads.
- Practice simulation disclosure is present.
- Project dialog supports previous and next navigation.
- Direct hash loading is implemented.
- Native buttons are used for gallery and case-study controls.
- Reduced-motion rules exist for current hover effects.
- Existing colors, portrait assets, email, LinkedIn, Upwork, and Fiverr links provide a usable brand base.

## Recruiter experience issues

- The strongest evidence appears too late. Recruiters see About, hiring modes, Services, and Tools before project proof.
- The hero has four competing actions plus navigation CTAs.
- Homepage sections repeat similar claims about data entry, checking, organization, and written updates.
- Ten projects are presented with too much visual equality, which weakens prioritization.
- Tools are shown as twelve equal tiles, including tools not supported by the case-study data.
- The About section emphasizes general traits before showing work evidence.
- Several sections use the same split-heading and card-grid rhythm.
- The current dark hero, dark workflow, and green contact band create multiple theme shifts.
- Project preview numbers are overlaid on screenshots, which competes with the evidence.

## Case-study issues

- The existing structure covers most required content but does not clearly label Input, Checks / QA, and Exceptions.
- Evidence is split into primary and collapsed groups, but not organized as Input, Process / Checks, Output.
- The lightbox does not provide previous and next image controls or a visible caption.
- Focus return from the lightbox is incomplete.
- The gallery loads only after a `details` toggle, which is efficient but needs stronger initialization and error handling.
- Hash routes work in code, but direct load, refresh, back behavior, and all ten projects still require browser QA.

## Accessibility and performance risks

- Homepage project cards are converted into `role="link"` elements instead of using native anchors.
- Image dimensions are not declared, which can contribute to layout shift.
- Mobile navigation and dialog focus behavior require browser verification.
- There is no explicit image error state.
- Many large screenshots need thumbnail-aware loading and lazy loading outside the selected evidence.
- Focus styles and color contrast need a full redesign pass.

## Recommended information architecture

1. Hero
2. Selected Work
3. Capabilities
4. How I Work
5. Tools
6. All Projects
7. About / Availability
8. Contact

## Selected Work recommendation

- `PROJ-003 Order Reconciliation`: strongest reconciliation narrative, two source datasets, formula checks, dashboard, exception queue, and the largest evidence set.
- `PROJ-010 Multi-Source Data Merge`: strongest master-data story with three sources, normalization, conflict handling, and a clear final customer master.
- `PROJ-002 Customer Data Cleanup`: strongest direct fit for Data Entry and CRM support, with raw data, mappings, QA, review queue, SOP, and detailed evidence.

Together these projects communicate the intended promise: organize messy operational data, validate it, isolate exceptions, document the work, and deliver a reliable output.

## Design direction

- Redesign mode: structural overhaul with strict evidence, route, and contact preservation.
- Design system: native HTML, CSS, and JavaScript with an editorial portfolio language.
- `DESIGN_VARIANCE: 6`
- `MOTION_INTENSITY: 3`
- `VISUAL_DENSITY: 4`
- One light theme, one restrained green accent, soft 12px media corners, pill-free content containers, and minimal motion limited to feedback and state change.
