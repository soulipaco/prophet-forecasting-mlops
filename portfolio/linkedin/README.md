# LinkedIn portfolio package

## Content summary

The eight-slide carousel tells one story: this repository turns Prophet forecasting into an
inspectable batch system. It moves from the coordination problem (`N` series x two targets), through
the Python/Databricks boundary and time-aware lifecycle, to reproducibility evidence, a native chart
from the deterministic synthetic run, deliberate exclusions, and a repository invitation.

## Design description

The deck uses a 1080 x 1350 portrait canvas for mobile readability. Ink and paper backgrounds
alternate to mark conceptual shifts. Blue represents forecast/model flow, teal marks boundaries and
completed states, and orange is reserved for cutoffs or deliberate decisions. Large left-aligned
headlines, generous whitespace, short supporting copy, and one main claim per slide create a clear
scroll rhythm. All architecture, lifecycle, and chart elements are editable PowerPoint objects; the
forecast chart is a native chart backed by the repository CSV.

## Files

- `prophet-forecasting-carousel.pptx`: editable eight-slide carousel.
- `carousel/slide-01.png` through `slide-08.png`: upload-ready 1080 x 1350 images.
- `main-image.png`: 1200 x 627 featured/social image.
- `carousel-montage.webp`: compact sequence preview.
- `source/generate_carousel.mjs`: artifact-tool source used to create the deck and images.
- `linkedin_copy.md`: post copy, profile copy, repository metadata, hashtags, and alt text.

Every numerical statement is a synthetic execution result and is traced in
`../../docs/claims_traceability.md`. The deck contains no business-impact or production-performance
claim.

