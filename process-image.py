import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from natsort import natsorted
from PIL import Image

from google import genai
from google.genai import types

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    PageBreak,
    Spacer,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT


# ============================================================
# Configuration
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found.\n"
        "Create a .env file containing:\n\n"
        "GEMINI_API_KEY=your_api_key_here"
    )

client = genai.Client(api_key=API_KEY)

# MODEL = "gemini-3.8-flash"
MODEL = "gemini-3.5-flash-lite"



IMAGE_DIR = Path("images")
OUTPUT_DIR = Path("output")
PAGE_OUTPUT_DIR = OUTPUT_DIR / "pages"

HTML_OUTPUT = OUTPUT_DIR / "clean_test_booklet.html"
PDF_OUTPUT = OUTPUT_DIR / "clean_test_booklet.pdf"

# Maximum image dimension sent to Gemini.
# 2000 is a reasonable compromise between OCR quality and payload size.
MAX_IMAGE_SIZE = 2000

# Number of retries for temporary API failures.
MAX_RETRIES = 3

# Small delay between successful requests.
# This is NOT our rate-limit handling mechanism.
REQUEST_DELAY = 1.0


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


# ============================================================
# HTML
# ============================================================

HTML_START = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>English Exercises</title>

<style>

@page {
    size: A4;
    margin: 1.5cm;
}

body {
    font-family: "Times New Roman", Times, serif;
    color: #111;
    line-height: 1.4;
    background: #f4f4f4;
    margin: 0;
    padding: 20px;
}

/* ========================================================
   Booklet container (natural document on screen)
   ======================================================== */

.booklet {
    background: white;
    max-width: 800px;
    margin: 0 auto 30px auto;
    padding: 40px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    box-sizing: border-box;
}

/* ========================================================
   Continuous flow & exercises
   ======================================================== */

.exercise,
.review-exercise {
    margin-bottom: 28px;
}

.exercise-title,
.question-text:first-child {
    margin-bottom: 20px;
    line-height: 1.55;
    break-after: avoid;
    page-break-after: avoid;
}

.exercise-number {
    font-weight: bold;
}

/* ========================================================
   Multiple-choice questions
   ======================================================== */

.question-block {
    margin-bottom: 24px;
    break-inside: avoid;
    page-break-inside: avoid;
}

.question-text {
    margin-bottom: 8px;
    line-height: 1.55;
}

.option {
    margin-left: 28px;
    margin-bottom: 5px;
}

/* ========================================================
   C / I questions
   ======================================================== */

.ci-question {
    margin-bottom: 20px;
    line-height: 1.55;
    break-inside: avoid;
    page-break-inside: avoid;
}

.ci-blank {
    display: inline-block;
    width: 105px;
    height: 1.1em;
    border-bottom: 1px solid #111;
    margin-right: 10px;
    vertical-align: baseline;
    box-sizing: border-box;
}

.ci-text {
    vertical-align: baseline;
}

/* ========================================================
   Blanks inside sentences
   ======================================================== */

.blank {
    display: inline-block;
    min-width: 90px;
    border-bottom: 1px solid #111;
}

/* ========================================================
   Review section & Page break rules
   ======================================================== */

.page-break {
    clear: both;
    display: block;
    height: 0;
    margin: 0;
    padding: 0;
    border: none;
    break-before: page !important;
    page-break-before: always !important;
}

.review-section {
    break-before: page !important;
    page-break-before: always !important;
}

.review-section > .review-exercise:first-child {
    break-before: page !important;
    page-break-before: always !important;
}

@media screen {
    .page-break {
        height: 1px;
        margin: 40px 0;
        background: transparent;
        border-top: 2px dashed #bbb;
        position: relative;
    }
    .page-break::after {
        content: "PAGE BREAK (Review Section)";
        position: absolute;
        top: -11px;
        left: 50%;
        transform: translateX(-50%);
        background: #fff;
        border: 1px solid #ccc;
        padding: 2px 10px;
        font-size: 11px;
        color: #666;
        border-radius: 3px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
}

/* ========================================================
   Print styles
   ======================================================== */

@media print {

    html, body {
        background: white !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }

    .booklet {
        display: block !important;
        max-width: none !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        border: none !important;
    }

    .page-break {
        display: block !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        visibility: hidden;
        break-before: page !important;
        page-break-before: always !important;
    }

    .review-section {
        break-before: page !important;
        page-break-before: always !important;
    }

    .review-section > .review-exercise:first-child {
        break-before: page !important;
        page-break-before: always !important;
    }

    .question-block,
    .ci-question {
        break-inside: avoid !important;
        page-break-inside: avoid !important;
    }

    .exercise-title {
        break-after: avoid !important;
        page-break-after: avoid !important;
    }

}

</style>
</head>

<body>
<div class="booklet">
"""


HTML_END = """
</div><!-- .booklet -->
</body>
</html>
"""


# ============================================================
# Gemini prompt
# ============================================================

PROMPT = """
Recreate this English textbook page as clean HTML for a NEW,
UNANSWERED worksheet.

Remove all handwriting, pen/pencil marks, circles, checkmarks,
corrections, highlighting, and handwritten answers.

Preserve all printed text, numbering, instructions, blanks,
underlines, and question order. Do NOT solve or correct anything.

There are ONLY TWO exercise types.

1. MULTIPLE CHOICE:

<div class="question-block">
  <div class="question-text">1. Question...</div>
  <div class="option">(A) ...</div>
  <div class="option">(B) ...</div>
  <div class="option">(C) ...</div>
  <div class="option">(D) ...</div>
</div>

Use ONLY divs. Never use ol, ul, or li.
For blanks inside sentences use <span class="blank"></span>.

2. C / I:

<div class="ci-question">
  <span class="ci-blank"></span>
  <span class="ci-text">1. Question...</span>
</div>

Do not write C or I.

Question headings: 

If the page contains an exercise heading such as:
EXERCISE 1: Underline the subjects...
or 
TOEFL EXERCISE 1 (Skills 1-5): Underline the subjects...
Then add <span class="exercise-number">EXERCISE 1:</span> Remaining text here...


HTML rules:
- Only use the classes shown above.
- Do not use <u>.
- Do not use text-decoration.
- Do not create CSS.
- Do not add answers.
- Do not add explanations.

Return ONLY:
<div class="page">...</div>

No Markdown, code fences, html/head/body tags.
"""


# ============================================================
# File handling
# ============================================================

def get_image_files():
    """Return all supported images in natural filename order."""

    files = [
        path
        for path in IMAGE_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    return natsorted(files)


def clean_gemini_response(text: str) -> str:
    """Remove accidental Markdown code fences."""

    text = text.strip()

    text = re.sub(
        r"^```(?:html)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    return text.strip()


# ============================================================
# Gemini
# ============================================================

def process_image(image_path: Path) -> str:
    """
    Send ONE image to Gemini.

    Important:
    No previous images, prompts, answers, or conversation history
    are sent with this request.
    """

    with Image.open(image_path) as original_image:

        # Work on a copy so we don't modify the source image.
        image = original_image.copy()

        # Convert unusual formats/modes.
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")

        # Resize only if necessary.
        image.thumbnail(
            (MAX_IMAGE_SIZE, MAX_IMAGE_SIZE),
            Image.Resampling.LANCZOS,
        )

        for attempt in range(1, MAX_RETRIES + 1):

            try:

                response = client.models.generate_content(
                    model=MODEL,
                    contents=[
                        PROMPT,
                        image,
                    ],
                    config=types.GenerateContentConfig(
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(
                            disable=True
                        )
                    ),
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return clean_gemini_response(response.text)

            except Exception as error:

                if attempt == MAX_RETRIES:
                    raise

                wait_time = 2 ** attempt

                print(
                    f"    Temporary error: {error}"
                )
                print(
                    f"    Retrying in {wait_time}s..."
                )

                time.sleep(wait_time)


# ============================================================
# Process all pages
# ============================================================

def process_pages():
    """
    Process each image independently.

    Already processed pages are skipped.
    """

    IMAGE_DIR.mkdir(exist_ok=True)
    PAGE_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    images = get_image_files()

    if not images:
        print(
            f"No images found in {IMAGE_DIR}/"
        )
        return []

    print(f"Found {len(images)} images.\n")

    processed_pages = []

    for index, image_path in enumerate(
        images,
        start=1,
    ):

        page_output = (
            PAGE_OUTPUT_DIR
            / f"{image_path.stem}.html"
        )

        # -----------------------------------------------
        # Already processed?
        # -----------------------------------------------

        if page_output.exists():

            print(
                f"[{index}/{len(images)}] "
                f"Skipping {image_path.name} "
                f"(already processed)"
            )

            processed_pages.append(page_output)
            continue

        print(
            f"[{index}/{len(images)}] "
            f"Processing {image_path.name}..."
        )

        try:

            html = process_image(image_path)

            page_output.write_text(
                html,
                encoding="utf-8",
            )

            processed_pages.append(
                page_output
            )

            print(
                f"    Saved: {page_output}"
            )

        except Exception as error:

            print(
                f"    FAILED: {error}"
            )

            # Continue to the next page instead of
            # killing the entire 100-page process.

        # Small delay after successful processing.
        if index < len(images):
            time.sleep(REQUEST_DELAY)

    return processed_pages


# ============================================================
# Section grouping
# ============================================================

def get_section_group(path: Path) -> str:
    """
    Determine the logical grouping for an exercise page.

    Review pages belonging to the same review set share a group
    (e.g., '5_review'), while standard exercises are 'regular'.
    """
    stem = path.stem.lower()
    match = re.search(r"(\d+)_review", stem)
    if match:
        return f"{match.group(1)}_review"
    if "_review" in stem:
        return "review"
    return "regular"


# ============================================================
# Generate HTML booklet
# ============================================================

def generate_html(processed_pages):
    """
    Combine generated exercise fragments into one continuous booklet.

    Normal exercises flow naturally across pages.
    Review question sections start on a new page, flow continuously,
    and are followed by a new page.
    """

    OUTPUT_DIR.mkdir(exist_ok=True)

    with HTML_OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as output:

        output.write(HTML_START)

        current_review_group = None

        for page_file in processed_pages:

            group = get_section_group(page_file)
            is_review = group != "regular"

            html = page_file.read_text(
                encoding="utf-8"
            )

            # Remove the outer .page wrapper generated by Gemini.
            html = re.sub(
                r'<div class="page">\s*',
                "",
                html,
                flags=re.IGNORECASE,
            )

            html = re.sub(
                r'\s*</div>\s*$',
                "",
                html,
                flags=re.IGNORECASE,
            )

            # ------------------------------------------------
            # Handle review section boundaries
            # ------------------------------------------------
            if is_review:
                if current_review_group != group:
                    # Transition into or between review groups
                    if current_review_group is not None:
                        output.write('\n</div><!-- review-section -->\n')
                    output.write('\n<div class="page-break"></div>\n')
                    output.write('\n<div class="review-section">\n')
                    current_review_group = group
            else:
                # Transition out of review section back to regular
                if current_review_group is not None:
                    output.write('\n</div><!-- review-section -->\n')
                    output.write('\n<div class="page-break"></div>\n')
                    current_review_group = None

            # ------------------------------------------------
            # Add the exercise
            # ------------------------------------------------
            container_cls = (
                "review-exercise"
                if is_review
                else "exercise"
            )

            output.write(f'\n<div class="{container_cls}">\n')
            output.write(html.strip())
            output.write('\n</div>\n')

        # Close review section if the booklet ends with one.
        if current_review_group is not None:
            output.write('\n</div><!-- review-section -->\n')

        output.write(HTML_END)

    print(
        f"\nHTML created: {HTML_OUTPUT}"
    )


# ============================================================
# Generate PDF
# ============================================================

def parse_html_to_flowables(html: str, styles) -> list:
    """
    Convert an exercise HTML fragment into ReportLab flowables,
    supporting both Multiple Choice and C/I exercises.
    """
    flowables = []

    # Clean wrappers
    html = re.sub(r"</?div class=\"page\">", "", html, flags=re.IGNORECASE)
    html = html.replace("<strong>", "<b>").replace("</strong>", "</b>")

    # Format blanks as underlined spaces
    html = re.sub(
        r'<span class="ci-blank">\s*</span>',
        '<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>&nbsp;&nbsp;',
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r'<span class="blank">\s*</span>',
        '<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>',
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r'<span class="exercise-number">(.*?)</span>',
        r'<b>\1</b>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Extract exercise title/header if present
    title_match = re.search(
        r'<div class="(?:exercise-title|question-text)">\s*(<b>.*?</b>.*?)</div>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if title_match:
        title_raw = title_match.group(1)
        title_clean = re.sub(r'</?(?:div|span)[^>]*>', '', title_raw).strip()
        title_clean = re.sub(r'\s+', ' ', title_clean)
        if title_clean:
            flowables.append(Paragraph(title_clean, styles["ExerciseTitle"]))
            flowables.append(Spacer(1, 8))

    # Match all CI questions
    ci_matches = re.findall(
        r'<div class="ci-question">(.*?)</div>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for ci_html in ci_matches:
        ci_clean = re.sub(r'</?(?:div|span)[^>]*>', '', ci_html).strip()
        ci_clean = re.sub(r'\s+', ' ', ci_clean)
        if ci_clean:
            flowables.append(
                KeepTogether([Paragraph(ci_clean, styles["CIQuestion"])])
            )

    # Match all Multiple Choice question blocks
    qb_matches = re.findall(
        r'<div class="question-block">(.*?)(?=<div class="question-block">|$)',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for qb_html in qb_matches:
        qt_match = re.search(
            r'<div class="question-text">(.*?)</div>',
            qb_html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        opt_matches = re.findall(
            r'<div class="option">(.*?)</div>',
            qb_html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        qb_flowables = []
        if qt_match:
            qt_clean = re.sub(r'</?(?:div|span)[^>]*>', '', qt_match.group(1)).strip()
            qt_clean = re.sub(r'\s+', ' ', qt_clean)
            if qt_clean:
                qb_flowables.append(Paragraph(qt_clean, styles["Question"]))
        for opt in opt_matches:
            opt_clean = re.sub(r'</?(?:div|span)[^>]*>', '', opt).strip()
            opt_clean = re.sub(r'\s+', ' ', opt_clean)
            if opt_clean:
                qb_flowables.append(Paragraph(opt_clean, styles["Option"]))
        if qb_flowables:
            flowables.append(KeepTogether(qb_flowables))
            flowables.append(Spacer(1, 6))

    # Fallback for generic text blocks if neither pattern matched
    if not ci_matches and not qb_matches:
        text_clean = re.sub(r'</?(?:div|span)[^>]*>', '', html).strip()
        text_clean = re.sub(r'\s+', ' ', text_clean)
        if text_clean:
            flowables.append(Paragraph(text_clean, styles["ExerciseText"]))

    return flowables


def html_to_pdf(processed_pages):
    """
    Generate a printable PDF directly from the generated
    HTML fragments.

    Normal exercises flow naturally across pages.
    Page breaks occur only when entering or leaving review sections.
    """

    doc = SimpleDocTemplate(
        str(PDF_OUTPUT),
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
        title="English Exercises",
    )

    base_styles = getSampleStyleSheet()

    exercise_text = ParagraphStyle(
        "ExerciseText",
        parent=base_styles["Normal"],
        fontName="Times-Roman",
        fontSize=11,
        leading=15,
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    exercise_title = ParagraphStyle(
        "ExerciseTitle",
        parent=exercise_text,
        fontName="Times-Bold",
        fontSize=12,
        leading=16,
        spaceAfter=10,
        keepWithNext=True,
    )

    question = ParagraphStyle(
        "Question",
        parent=exercise_text,
        fontSize=11,
        leading=15,
        spaceAfter=6,
        keepWithNext=True,
    )

    option = ParagraphStyle(
        "Option",
        parent=exercise_text,
        leftIndent=24,
        spaceAfter=3,
    )

    ci_question = ParagraphStyle(
        "CIQuestion",
        parent=exercise_text,
        spaceAfter=8,
    )

    styles = {
        "ExerciseText": exercise_text,
        "ExerciseTitle": exercise_title,
        "Question": question,
        "Option": option,
        "CIQuestion": ci_question,
    }

    story = []
    prev_group = None

    for page_index, page_file in enumerate(processed_pages):

        group = get_section_group(page_file)

        # Separate sections: only break page when crossing between
        # regular exercises and review sections (or different review sets).
        if page_index > 0:
            if prev_group != group:
                story.append(PageBreak())
            else:
                story.append(Spacer(1, 16))

        prev_group = group

        html = page_file.read_text(encoding="utf-8")
        flowables = parse_html_to_flowables(html, styles)
        story.extend(flowables)

    doc.build(story)

    print(
        f"PDF created: {PDF_OUTPUT}"
    )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("English Exercise Recreator")
    print("=" * 60)
    print()

    processed_pages = process_pages()

    if not processed_pages:
        print(
            "\nNo pages were successfully processed."
        )
        return

    print()
    print("Generating output files...")

    generate_html(processed_pages)

    html_to_pdf(processed_pages)

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)
    print()
    print(f"HTML: {HTML_OUTPUT}")
    print(f"PDF:  {PDF_OUTPUT}")


if __name__ == "__main__":
    main()