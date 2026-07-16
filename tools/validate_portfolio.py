"""Validate public portfolio links, assets, evidence, and safety rules."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import unquote

from PIL import Image

ROOT = Path(__file__).parents[1]
MARKDOWN_FILES = [
    ROOT / "README.md",
    *sorted((ROOT / "docs").glob("*.md")),
    *sorted((ROOT / "portfolio").rglob("*.md")),
]
PUBLIC_SUFFIXES = {".csv", ".json", ".md", ".mjs", ".py", ".toml", ".yaml", ".yml"}
EXCLUDED_PARTS = {".databricks", ".git", ".venv", "build", "dist", "__pycache__"}
PUBLIC_TEXT_FILES = [
    file
    for file in ROOT.rglob("*")
    if file.is_file()
    and file != ROOT / "tools" / "validate_portfolio.py"
    and file.suffix.lower() in PUBLIC_SUFFIXES
    and not EXCLUDED_PARTS.intersection(file.parts)
]
PUBLIC_TEXT_FILES.extend([ROOT / ".gitignore"])

EXPECTED_ASSETS = {
    "hero": (1600, 560),
    "architecture": (1600, 900),
    "lifecycle": (1600, 600),
    "synthetic_forecast": (1600, 900),
}

FORBIDDEN_PATTERNS = {
    "Databricks personal access token": re.compile(r"dapi[a-zA-Z0-9]{20,}"),
    "Databricks workspace URL": re.compile(r"https://dbc-[a-zA-Z0-9-]+\.cloud\.databricks\.com"),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "local Windows user path": re.compile(r"[A-Z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    "stale target placeholder": re.compile(r"<TARGET_PROJECT_PATH>"),
    "unrelated reference name": re.compile(r"marvel[-_ ]characters?", re.IGNORECASE),
    "private-source narrative": re.compile(r"confidential|anonymi[sz]|saniti[sz]", re.IGNORECASE),
}


def validate_markdown_links() -> list[str]:
    errors: list[str] = []
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for file in MARKDOWN_FILES:
        if not file.exists():
            errors.append(f"missing Markdown file: {file.relative_to(ROOT)}")
            continue
        for target in link_pattern.findall(file.read_text(encoding="utf-8")):
            target = target.strip().split(maxsplit=1)[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = unquote(target.split("#", maxsplit=1)[0])
            resolved = (file.parent / relative).resolve()
            if not resolved.exists():
                errors.append(f"broken link in {file.relative_to(ROOT)}: {target}")
    return errors


def validate_assets() -> list[str]:
    errors: list[str] = []
    asset_dir = ROOT / "assets" / "portfolio"
    manifest_path = asset_dir / "visual_manifest.json"
    if not manifest_path.exists():
        return ["missing visual manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for stem, dimensions in EXPECTED_ASSETS.items():
        for extension in ("svg", "png"):
            path = asset_dir / f"{stem}.{extension}"
            if not path.exists() or path.stat().st_size == 0:
                errors.append(f"missing or empty asset: {path.relative_to(ROOT)}")
        png = asset_dir / f"{stem}.png"
        if png.exists():
            with Image.open(png) as image:
                if image.size != dimensions:
                    errors.append(f"wrong dimensions for {png.relative_to(ROOT)}: {image.size}")
                if any(key in image.info for key in ("Author", "Description", "Comment", "Software")):
                    errors.append(f"descriptive PNG metadata remains in {png.relative_to(ROOT)}")
        if tuple(manifest["assets"][stem]["dimensions"]) != dimensions:
            errors.append(f"manifest dimension mismatch for {stem}")
    csv_path = asset_dir / "synthetic_forecast.csv"
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    if digest != manifest.get("forecast_csv_sha256"):
        errors.append("synthetic forecast CSV hash does not match the visual manifest")
    collection = manifest.get("collection", {})
    if collection != {
        "source_rows": 430,
        "series": 2,
        "targets": 2,
        "completed_fits": 4,
        "failed_fits": 0,
        "forecast_rows": 832,
        "backtest_rows": 84,
    }:
        errors.append("synthetic collection evidence differs from the approved public baseline")
    return errors


def validate_public_text() -> list[str]:
    errors: list[str] = []
    for file in PUBLIC_TEXT_FILES:
        text = file.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} found in {file.relative_to(ROOT)}")
    return errors


def validate_linkedin_assets() -> list[str]:
    errors: list[str] = []
    linkedin = ROOT / "portfolio" / "linkedin"
    expected = {linkedin / "main-image.png": (1200, 627)}
    expected.update({linkedin / "carousel" / f"slide-{index:02d}.png": (1080, 1350) for index in range(1, 9)})
    for file, dimensions in expected.items():
        if not file.exists():
            errors.append(f"missing LinkedIn image: {file.relative_to(ROOT)}")
            continue
        with Image.open(file) as image:
            if image.size != dimensions:
                errors.append(f"wrong dimensions for {file.relative_to(ROOT)}: {image.size}")

    pptx = linkedin / "prophet-forecasting-carousel.pptx"
    if not pptx.exists() or pptx.stat().st_size == 0:
        errors.append("missing or empty LinkedIn carousel PPTX")
        return errors
    with zipfile.ZipFile(pptx) as archive:
        xml_text = "\n".join(
            archive.read(name).decode("utf-8", errors="ignore")
            for name in archive.namelist()
            if name.endswith((".xml", ".rels"))
        )
    for label, pattern in FORBIDDEN_PATTERNS.items():
        if pattern.search(xml_text):
            errors.append(f"{label} found inside the LinkedIn carousel PPTX")
    return errors


def main() -> None:
    errors = [
        *validate_markdown_links(),
        *validate_assets(),
        *validate_public_text(),
        *validate_linkedin_assets(),
    ]
    if errors:
        raise SystemExit("Portfolio validation failed:\n- " + "\n- ".join(errors))
    print(f"Portfolio validation passed: {len(MARKDOWN_FILES)} Markdown files, 13 images, 1 PPTX, 0 safety hits.")


if __name__ == "__main__":
    main()
