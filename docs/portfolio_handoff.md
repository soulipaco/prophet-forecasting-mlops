# Portfolio handoff

## Created

- `assets/portfolio/`: hero, implemented architecture, lifecycle, synthetic forecast SVG/PNG, source
  forecast CSV, and visual manifest.
- `docs/architecture.md`: implemented architecture replacing the stale target proposal.
- `docs/claims_traceability.md`: evidence and approved wording for public claims.
- `docs/portfolio_audit.md`: concise presentation and public-safety audit.
- `docs/validation_report.md`: local, visual, presentation, safety, and Databricks-boundary results.
- `docs/visual_identity.md`: palette, typography, chart contract, and asset registry.
- `portfolio/linkedin/`: main image, eight-slide PNG carousel, editable PPTX, source, copy, alt text,
  and package guide.
- `tools/generate_portfolio_assets.py`: deterministic visual generation through the actual package.
- `tools/validate_portfolio.py`: link, asset, evidence, metadata, PPTX, and public-safety checks.

## Modified

- `README.md`: evidence-first portfolio story, diagrams, commands, scope, and navigation.
- `.github/workflows/ci.yml`: portfolio dependency, source-tool checks, and portfolio validation.
- `.gitignore`: removed an irrelevant public reference entry.
- `pyproject.toml` and `uv.lock`: added a separate portfolio-only Matplotlib/Pillow extra.

`docs/target_architecture.md` was replaced by `docs/architecture.md`; no forecasting package,
configuration value, Databricks task behavior, or test expectation was changed.

## Deliberately excluded

- online serving and request-time endpoints;
- a model-registry entry for every series/target fit;
- automated promotion, retraining triggers, monitoring, or alerting;
- a production schedule or continuous deployment workflow;
- production ingestion and real-data screenshots;
- business-impact, accuracy-improvement, scale, cost, or deployment-success claims without evidence;
- issue templates, contribution boilerplate, changelog, release history, license changes, and extra
  badges that do not improve this repository's current use.

## Suggested commit breakdown

1. `docs: rebuild portfolio narrative and implemented architecture`
   - README, audit, architecture, claims, identity, validation, and handoff documents.
2. `chore: add reproducible portfolio visuals and validation`
   - asset generator, generated GitHub visuals, portfolio extra, lock update, and CI checks.
3. `docs: add LinkedIn carousel and publishing copy`
   - main image, slide exports, editable PPTX, generator source, copy, and alt text.

No commit has been created; this breakdown is only a review recommendation.

## Owner-only actions

- Review and commit the changes in the preferred grouping.
- Push only after the diff is approved.
- Replace the GitHub repository description with the recommendation in
  `portfolio/linkedin/linkedin_copy.md` and confirm the suggested topics.
- Set `portfolio/linkedin/main-image.png` as the social preview if desired.
- Re-authenticate Databricks and re-run all three bundle validations before making a current
  deployment claim.
- Publish the LinkedIn post/carousel manually after final wording review.
