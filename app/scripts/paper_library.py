from __future__ import annotations

import json
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "RCMLStoryApp/1.0 (+https://github.com/github/copilot)"
RESEARCH_SOURCE = Path("research/05_Datasets_and_Similar_Research.md")
PAPER_SECTIONS = {
    "Core Papers Directly at the Intersection of ML + Radiative Cooling": "core",
    "Broader ML + Materials Design (Methodological Foundation)": "foundation",
    "Recent Papers Not Cited But Highly Relevant": "recent",
}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "paper"


def _clean_markdown(text: str) -> str:
    return re.sub(r"[*`_]", "", text).strip()


def _extract_title(cell: str) -> str:
    quoted = re.search(r'"([^"]+)"', cell)
    if quoted:
        return quoted.group(1).strip()
    return _clean_markdown(cell)


def _extract_authors(cell: str) -> str:
    cleaned = _clean_markdown(cell)
    if '"' in cleaned:
        return cleaned.split('"', 1)[0].strip().strip(". ")
    return ""


def _extract_venue(cell: str) -> str:
    italic = re.findall(r"\*([^*]+)\*", cell)
    return italic[-1].strip() if italic else ""


def _normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _parse_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _parse_table(lines: list[str], start_index: int) -> tuple[list[str], list[list[str]], int]:
    headers = _parse_markdown_row(lines[start_index])
    rows: list[list[str]] = []
    index = start_index + 2
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped.startswith("|"):
            break
        rows.append(_parse_markdown_row(lines[index]))
        index += 1
    return headers, rows, index


def _load_cache(cache_path: Path) -> dict[str, dict]:
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_cache(cache_path: Path, cache: dict[str, dict]) -> None:
    cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=True), encoding="utf-8")


def _openalex_lookup(title: str, year: int | None) -> dict | None:
    query = urllib.parse.quote(title)
    request = urllib.request.Request(
        f"https://api.openalex.org/works?search={query}&per-page=5",
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    target = _normalize_title(title)
    best_score = -1
    best_match: dict | None = None
    for work in payload.get("results", []):
        candidate_title = _normalize_title(work.get("display_name", ""))
        score = 0
        if candidate_title == target:
            score += 100
        elif target and target in candidate_title:
            score += 70
        elif candidate_title and candidate_title in target:
            score += 40
        if year and work.get("publication_year") == year:
            score += 10
        if score > best_score:
            best_score = score
            best_match = work

    if not best_match or best_score < 40:
        return None

    authors = ", ".join(
        authorship.get("author", {}).get("display_name", "")
        for authorship in best_match.get("authorships", [])[:5]
        if authorship.get("author", {}).get("display_name")
    )
    best_location = best_match.get("best_oa_location") or {}
    primary_location = best_match.get("primary_location") or {}
    source = (primary_location.get("source") or {}).get("display_name") or (best_location.get("source") or {}).get("display_name")
    landing_page = best_location.get("landing_page_url") or primary_location.get("landing_page_url") or best_match.get("doi")
    pdf_url = best_location.get("pdf_url")
    oa_url = (best_match.get("open_access") or {}).get("oa_url")

    return {
        "title": best_match.get("display_name") or title,
        "authors": authors,
        "year": best_match.get("publication_year"),
        "venue": source,
        "doi": best_match.get("doi"),
        "officialUrl": landing_page,
        "openAccessPdfUrl": pdf_url or (oa_url if isinstance(oa_url, str) and oa_url.lower().endswith(".pdf") else None),
        "openAccessUrl": oa_url,
    }


def _download_pdf(url: str, destination: Path) -> int | None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if "pdf" not in content_type and ".pdf" not in url.lower():
                return None
            payload = response.read()
    except (urllib.error.URLError, TimeoutError):
        return None

    destination.write_bytes(payload)
    return len(payload)


def _public_path(app_public_dir: Path, path: Path) -> str:
    return "/" + path.relative_to(app_public_dir).as_posix()


def _collect_paper_seeds(root: Path) -> list[dict]:
    lines = (root / RESEARCH_SOURCE).read_text(encoding="utf-8").splitlines()
    current_heading = ""
    papers: list[dict] = []
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("### "):
            current_heading = stripped[4:].strip()
            index += 1
            continue

        if current_heading in PAPER_SECTIONS and stripped.startswith("| Paper |"):
            _, rows, next_index = _parse_table(lines, index)
            for row in rows:
                if len(row) < 4:
                    continue
                papers.append(
                    {
                        "title": _extract_title(row[0]),
                        "authors": _extract_authors(row[0]),
                        "venue": _extract_venue(row[0]),
                        "year": int(row[1]) if row[1].isdigit() else None,
                        "summary": row[2].strip(),
                        "citationCount": row[3].strip(),
                        "category": PAPER_SECTIONS[current_heading],
                        "sourcePath": RESEARCH_SOURCE.as_posix(),
                    }
                )
            index = next_index
            continue

        index += 1

    unique: dict[str, dict] = {}
    for paper in papers:
        key = _normalize_title(paper["title"])
        if key not in unique:
            unique[key] = paper
    return list(unique.values())


def build_paper_library(root: Path, output_dir: Path, app_public_dir: Path) -> list[dict]:
    paper_dir = output_dir / "paper-pdfs"
    cache_path = output_dir / "paper-library-cache.json"
    legacy_generated_dir = output_dir / "pdfs"
    if legacy_generated_dir.exists():
        shutil.rmtree(legacy_generated_dir)

    paper_dir.mkdir(parents=True, exist_ok=True)
    cache = _load_cache(cache_path)
    papers: list[dict] = []

    for index, seed in enumerate(_collect_paper_seeds(root), start=1):
        slug = _slugify(seed["title"])
        cached = cache.get(slug, {})
        has_resolved_source = bool(
            cached.get("officialUrl")
            or cached.get("doi")
            or cached.get("openAccessPdfUrl")
            or cached.get("openAccessUrl")
        )
        year_mismatch = seed.get("year") is not None and cached.get("year") not in (None, seed.get("year"))

        if not cached.get("title") or (year_mismatch and not has_resolved_source):
            resolved = _openalex_lookup(seed["title"], seed.get("year")) or {}
            cached = {
                "title": resolved.get("title", seed["title"]),
                "authors": resolved.get("authors") or seed.get("authors") or "Unknown / unresolved",
                "year": resolved.get("year") or seed.get("year"),
                "venue": resolved.get("venue") or seed.get("venue") or "Unknown venue",
                "doi": resolved.get("doi"),
                "officialUrl": resolved.get("officialUrl") or resolved.get("openAccessUrl"),
                "openAccessPdfUrl": resolved.get("openAccessPdfUrl"),
                "openAccessUrl": resolved.get("openAccessUrl"),
            }
            cache[slug] = cached

        downloaded_path: str | None = None
        size_bytes: int | None = None
        pdf_destination = paper_dir / f"{index:02d}-{slug}.pdf"
        pdf_url = cached.get("openAccessPdfUrl")
        if pdf_url:
            if not pdf_destination.exists():
                _download_pdf(pdf_url, pdf_destination)
            if pdf_destination.exists():
                downloaded_path = _public_path(app_public_dir, pdf_destination)
                size_bytes = pdf_destination.stat().st_size

        official_url = cached.get("officialUrl") or cached.get("openAccessUrl") or cached.get("doi")
        status = "downloaded" if downloaded_path else "open-access-link" if official_url else "citation-only"

        papers.append(
            {
                "id": f"paper-{index:02d}",
                "title": cached.get("title", seed["title"]),
                "authors": cached.get("authors") or seed.get("authors") or "Unknown / unresolved",
                "year": cached.get("year") or seed.get("year"),
                "venue": cached.get("venue") or seed.get("venue") or "Unknown venue",
                "category": seed["category"],
                "summary": seed["summary"],
                "citationCount": seed["citationCount"],
                "doi": cached.get("doi"),
                "officialUrl": official_url,
                "openAccessPdfUrl": pdf_url,
                "downloadedPdfPath": downloaded_path,
                "pdfSizeBytes": size_bytes,
                "status": status,
                "sourcePath": seed["sourcePath"],
            }
        )

    _save_cache(cache_path, cache)
    return papers
