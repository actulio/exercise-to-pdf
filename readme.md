Absolutely — here's the **entire `README.md`**, with no extra explanation outside it.

````markdown
# English Exercise Recreator

A small Python script for turning photos/scans of answered English textbook exercises into clean, unanswered, printable exercises.

The script:

1. Reads textbook photos from `images/`
2. Sends each image independently to Gemini
3. Removes handwritten answers, markings, circles, etc.
4. Recreates the exercise as clean HTML
5. Saves each generated page locally
6. Combines all pages into one HTML booklet
7. Generates a printable PDF locally

The project is intentionally simple and is designed for personal use.

---

## Project Structure

```text
english-exercises/
│
├── images/
│   ├── 1.jpg
│   ├── 2.jpg
│   ├── 3.jpg
│   └── ...
│
├── output/
│   ├── pages/
│   │   ├── 1.html
│   │   ├── 2.html
│   │   └── ...
│   │
│   ├── clean_test_booklet.html
│   └── clean_test_booklet.pdf
│
├── .env
├── .gitignore
├── process.py
├── requirements.txt
└── README.md
```
````

The `output/` directory is created automatically by the script.

---

# Requirements

You need:

- Python 3.10 or newer
- A Gemini API key
- Internet access while processing the images

The project uses:

- Google Gemini API
- Pillow
- natsort
- python-dotenv
- ReportLab

---

# 1. Install Python

Check whether Python is already installed:

```bash
python --version
```

On some systems, use:

```bash
python3 --version
```

You should see something like:

```text
Python 3.12.5
```

Python 3.10 or newer is recommended.

If Python is not installed, download it from:

https://www.python.org/downloads/

---

# 2. Clone or download the project

If the project is in Git:

```bash
git clone <repository-url>
cd english-exercises
```

Or simply download/extract the project and open a terminal inside its directory.

You should be in the directory containing:

```text
process.py
requirements.txt
README.md
```

Check with:

```bash
ls
```

On Windows:

```powershell
dir
```

---

# 3. Create a Python virtual environment

A virtual environment keeps this project's Python dependencies separate from the rest of your computer.

## macOS / Linux

From the project directory:

```bash
python3 -m venv .venv
```

This creates:

```text
.venv/
```

Activate it:

```bash
source .venv/bin/activate
```

Your terminal should now look something like:

```text
(.venv) user@computer english-exercises %
```

The `(.venv)` means the virtual environment is active.

---

## Windows

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Your terminal should show:

```text
(.venv) C:\...\english-exercises>
```

---

# 4. Activating the virtual environment later

You need to activate the virtual environment whenever you open a new terminal and want to run the program.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\activate
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

---

# 5. Deactivating the virtual environment

When you're finished:

```bash
deactivate
```

This does not delete anything.

It simply returns your terminal to the normal Python environment.

You can activate it again later.

---

# 6. Install the dependencies

Make sure the virtual environment is activated.

You should see:

```text
(.venv)
```

in your terminal.

Then run:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains:

```text
google-genai
Pillow
natsort
python-dotenv
reportlab
```

If `pip` doesn't work, try:

```bash
python -m pip install -r requirements.txt
```

or on macOS/Linux:

```bash
python3 -m pip install -r requirements.txt
```

---

# 7. Gemini API key

The program uses Gemini to understand the textbook photos.

Create an API key through Google AI Studio:

https://aistudio.google.com/

After creating the key, create a file named:

```text
.env
```

in the project root.

The project should look like:

```text
english-exercises/
├── .env
├── process.py
├── requirements.txt
└── ...
```

Put this inside `.env`:

```env
GEMINI_API_KEY=your_api_key_here
```

For example:

```env
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxx
```

Do not add quotes unless your key requires them.

---

# 8. Protect your API key

Never commit your API key to Git.

Create a `.gitignore` file containing:

```gitignore
.venv/
.env
__pycache__/
output/
```

This prevents:

- the virtual environment
- your API key
- Python cache files
- generated output

from being committed.

---

# 9. Add the textbook photos

Put the textbook photos inside:

```text
images/
```

For example:

```text
images/
├── 1.jpg
├── 2.jpg
├── 3.jpg
├── 4.jpg
├── 5.jpg
├── 6.jpg
└── ...
```

Supported image formats:

```text
.jpg
.jpeg
.png
.webp
```

Numerical filenames are recommended.

For example:

```text
1.jpg
2.jpg
3.jpg
...
9.jpg
10.jpg
11.jpg
```

The program uses natural sorting, so `10.jpg` correctly comes after `9.jpg`.

---

# 10. Image quality

The photos should be reasonably clear.

The program automatically resizes large images before sending them to Gemini.

The default setting is:

```python
MAX_IMAGE_SIZE = 2000
```

This means the longest side of an image will be reduced to approximately 2000 pixels if it is larger than that.

For example:

```text
Original:
4000 × 6000

Sent to Gemini:
1333 × 2000
```

The original image is not modified.

---

## Why resize the images?

The goal is to keep enough resolution for Gemini to read the text while avoiding unnecessarily large image payloads.

For normal textbook photos, 2000 pixels on the longest side should be a reasonable starting point.

If OCR quality isn't good enough, try:

```python
MAX_IMAGE_SIZE = 2500
```

or:

```python
MAX_IMAGE_SIZE = 3000
```

Larger images may take longer to process and can increase API usage.

---

# 11. Run the program

Make sure the virtual environment is active:

```bash
source .venv/bin/activate
```

on macOS/Linux, or:

```powershell
.venv\Scripts\activate
```

on Windows.

Then run:

```bash
python process.py
```

You should see something similar to:

```text
============================================================
English Exercise Recreator
============================================================

Found 100 images.

[1/100] Processing 1.jpg...
    Saved: output/pages/1.html

[2/100] Processing 2.jpg...
    Saved: output/pages/2.html

[3/100] Processing 3.jpg...
    Saved: output/pages/3.html

...

[100/100] Processing 100.jpg...
    Saved: output/pages/100.html

Generating output files...

HTML created: output/clean_test_booklet.html
PDF created: output/clean_test_booklet.pdf

============================================================
DONE
============================================================
```

---

# 12. Output

After the program finishes:

```text
output/
├── pages/
│   ├── 1.html
│   ├── 2.html
│   ├── 3.html
│   └── ...
│
├── clean_test_booklet.html
└── clean_test_booklet.pdf
```

---

# 13. Individual generated pages

Every textbook photo gets its own HTML file.

For example:

```text
images/42.jpg
```

produces:

```text
output/pages/42.html
```

This is useful because you can inspect individual pages without regenerating the entire book.

---

# 14. HTML booklet

The complete HTML booklet is:

```text
output/clean_test_booklet.html
```

Open it in Chrome, Firefox, Safari, or another browser.

The document is configured for A4 paper.

You can print it directly:

```text
Print → Paper Size → A4
```

or save it as a PDF from the browser.

---

# 15. PDF booklet

The script also generates:

```text
output/clean_test_booklet.pdf
```

The PDF is generated locally using ReportLab.

Gemini does not generate the PDF.

Gemini is only used to understand the textbook image and recreate the exercise content.

Python handles the final PDF generation.

---

# 16. Important: API usage and context

One of the main goals of this project is to avoid unnecessary Gemini usage.

Each image is processed independently.

For every page, Gemini receives only:

```text
Current image
+
Short prompt
```

It does NOT receive:

```text
Previous images
Previous questions
Previous Gemini responses
The entire textbook
Generated HTML from previous pages
A growing conversation history
```

For example, when processing page 50, Gemini has no knowledge of pages 1–49.

This is intentional.

The exercises follow a small number of recurring structures, so there is no reason to repeatedly send previous pages as context.

---

# 17. No unnecessary context

The program does not use a Gemini chat session.

Instead, each request is independent:

```python
response = client.models.generate_content(
    model=MODEL,
    contents=[
        image,
        PROMPT,
    ],
)
```

This means the request contains only:

1. The current image
2. The instructions needed to process that image

Nothing else is carried between requests.

This helps keep the project simple and avoids unnecessary context.

---

# 18. Local caching

The program saves the Gemini result for every page:

```text
output/pages/1.html
output/pages/2.html
output/pages/3.html
...
```

If you run the program again, existing pages are skipped.

For example:

```text
[1/100] Skipping 1.jpg (already processed)
[2/100] Skipping 2.jpg (already processed)
[3/100] Skipping 3.jpg (already processed)
```

This means the same image is not unnecessarily sent to Gemini again.

---

# 19. Why caching is useful

Imagine you have 100 pages:

```text
Pages 1–80  → successful
Page 81     → API error
Pages 82–100 → successful
```

You can simply run:

```bash
python process.py
```

again.

The program will skip the pages that already have results and process the missing page.

This prevents you from paying for or waiting for the same 99 images again.

---

# 20. Retry behavior

Temporary API errors can happen.

The script retries failed requests up to:

```python
MAX_RETRIES = 3
```

The delay increases between attempts:

```text
Attempt 1 → wait 2 seconds
Attempt 2 → wait 4 seconds
Attempt 3 → fail
```

If a page still fails, the program prints the error and continues processing the remaining pages.

For example:

```text
[37/100] Processing 37.jpg...
    Temporary error: ...
    Retrying in 2s...

    Temporary error: ...
    Retrying in 4s...

    FAILED: ...
```

The other pages will still be processed.

---

# 21. Request delay

The script also has:

```python
REQUEST_DELAY = 1.0
```

This adds a small delay between successful requests.

This is not intended to guarantee compliance with Gemini's current rate limits.

If necessary, increase it:

```python
REQUEST_DELAY = 2.0
```

or:

```python
REQUEST_DELAY = 4.0
```

The exact API limits depend on the Gemini model and your account/API tier.

---

# 22. What Gemini does

Gemini is instructed to reconstruct the exercise rather than solve it.

For example, suppose the original page contains:

```text
1. She ______ to school every day.

(A) go
(B) goes ✓
(C) going
(D) gone
```

The desired result is:

```text
1. She ______ to school every day.

(A) go
(B) goes
(C) going
(D) gone
```

The checkmark is removed.

Gemini is also instructed to remove:

- handwriting
- pencil marks
- pen marks
- circles around answers
- checkmarks
- corrections
- highlighting
- handwritten answers

It should preserve:

- printed text
- question numbers
- answer choices
- blanks
- instructions
- underlined sections
- the structure of the exercise

It should not:

- solve the exercise
- add answers
- explain the questions
- rewrite the English
- correct the textbook's English

---

# 23. Exercise types

The prompt currently supports the recurring exercise structures used by the book.

For multiple-choice questions, it uses:

```html
<div class="question-block">
  Question text

  <ol class="options-list">
    <li>Option A</li>
    <li>Option B</li>
    <li>Option C</li>
    <li>Option D</li>
  </ol>
</div>
```

For written-expression/error-identification exercises, underlined sections are represented as:

```html
<span class="choice-item">
  <span class="text">underlined text</span>
  <span class="label">A</span>
</span>
```

Blanks are represented as:

```html
<span class="blank">________________</span>
```

If the book has another recurring exercise type, the Gemini prompt can be modified to explicitly describe it.

---

# 24. If a page is wrong

Suppose page 37 doesn't look right.

Delete only its cached result:

### macOS/Linux

```bash
rm output/pages/37.html
```

### Windows PowerShell

```powershell
Remove-Item output/pages/37.html
```

Then run:

```bash
python process.py
```

The script will:

- skip pages that already exist
- process page 37 again
- regenerate the final HTML
- regenerate the final PDF

Only page 37 needs to be sent to Gemini again.

---

# 25. If you want to completely regenerate everything

Delete the entire output directory.

### macOS/Linux

```bash
rm -rf output
```

### Windows PowerShell

```powershell
Remove-Item -Recurse -Force output
```

Then:

```bash
python process.py
```

This will process every image again.

**Be careful:** doing this means every page will be sent to Gemini again.

---

# 26. Starting from scratch

If you're setting up the project on a new computer:

```bash
git clone <repository-url>
cd english-exercises
```

Create the virtual environment:

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
GEMINI_API_KEY=your_api_key_here
```

Put the textbook images in:

```text
images/
```

Then run:

```bash
python process.py
```

---

# 27. Typical day-to-day usage

After the project is already configured, the normal workflow is simply:

### 1. Open a terminal

Go to the project:

```bash
cd english-exercises
```

### 2. Activate the virtual environment

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

### 3. Add or replace images

Put the textbook photos in:

```text
images/
```

### 4. Run

```bash
python process.py
```

### 5. Open the result

```text
output/clean_test_booklet.pdf
```

or:

```text
output/clean_test_booklet.html
```

### 6. Deactivate when finished

```bash
deactivate
```

---

# 28. Changing the Gemini model

The model is configured near the top of `process.py`:

```python
MODEL = "gemini-2.5-flash"
```

If you want to use another compatible Gemini model, change this value.

For example:

```python
MODEL = "your-model-name"
```

The rest of the program does not need to change.

---

# 29. Changing image size

The image size is configured here:

```python
MAX_IMAGE_SIZE = 2000
```

Possible values:

```python
MAX_IMAGE_SIZE = 1500
```

```python
MAX_IMAGE_SIZE = 2000
```

```python
MAX_IMAGE_SIZE = 2500
```

```python
MAX_IMAGE_SIZE = 3000
```

Start with 2000.

If Gemini has trouble reading small text, increase it.

If processing is unnecessarily slow, decrease it.

---

# 30. Changing the request delay

The delay is configured here:

```python
REQUEST_DELAY = 1.0
```

For example:

```python
REQUEST_DELAY = 2.0
```

means the script waits approximately two seconds between successful requests.

Again, this is only a small delay. It is not a replacement for proper API rate-limit handling.

---

# 31. Changing the retry count

The retry count is configured here:

```python
MAX_RETRIES = 3
```

For example:

```python
MAX_RETRIES = 5
```

would allow more attempts before giving up on a page.

---

# 32. Troubleshooting

## `GEMINI_API_KEY not found`

You probably don't have a `.env` file in the project directory.

Make sure this exists:

```text
.env
```

and contains:

```env
GEMINI_API_KEY=your_api_key_here
```

Also make sure you're running the script from the project directory.

---

## `ModuleNotFoundError`

For example:

```text
ModuleNotFoundError: No module named 'PIL'
```

Make sure the virtual environment is activated:

```bash
source .venv/bin/activate
```

or on Windows:

```powershell
.venv\Scripts\activate
```

Then reinstall:

```bash
pip install -r requirements.txt
```

---

## No images found

Make sure the images are inside:

```text
images/
```

and have one of these extensions:

```text
.jpg
.jpeg
.png
.webp
```

For example:

```text
images/1.jpg
```

---

## Gemini produces an incorrect page

First, check the original photo.

The most common causes are:

- blurry image
- text too small
- poor lighting
- page partially cut off
- handwriting covering printed text
- unusual page layout

Try increasing:

```python
MAX_IMAGE_SIZE = 2500
```

or:

```python
MAX_IMAGE_SIZE = 3000
```

Then delete the affected cached page and run the script again.

---

## PDF doesn't look exactly like the HTML

The PDF is generated with ReportLab and is intentionally simple.

The HTML renderer has more control over browser layout and CSS.

If the ReportLab PDF doesn't look good for a particular exercise, open:

```text
output/clean_test_booklet.html
```

in your browser and use:

```text
Print → Save as PDF
```

The browser may produce a better layout.

---

# 33. Why the project uses both HTML and PDF

The two outputs have different purposes.

### HTML

```text
clean_test_booklet.html
```

Advantages:

- Better CSS support
- Easy to inspect
- Easy to modify
- Browser printing usually looks good
- Easy to adjust formatting

### PDF

```text
clean_test_booklet.pdf
```

Advantages:

- Ready to send/print
- Layout is fixed
- Doesn't depend on the browser
- Convenient for sharing

The HTML is the more flexible source, while the PDF is the convenient final document.

---

# 34. Cost-conscious design

The project is deliberately designed so that Gemini only handles the part that actually requires AI.

### Gemini handles

```text
Photo
  ↓
Read the exercise
  ↓
Understand its structure
  ↓
Remove handwritten answers
  ↓
Produce clean HTML
```

### Python handles

```text
Image resizing
       ↓
Caching
       ↓
Retrying
       ↓
Saving pages
       ↓
Combining pages
       ↓
HTML generation
       ↓
PDF generation
```

There is no reason to use Gemini for the final PDF generation, page assembly, or other deterministic tasks.

---

# 35. No accumulated Gemini context

The program does not maintain a conversation with Gemini.

Every request is effectively:

```text
Request 1:
    image 1 + prompt

Request 2:
    image 2 + prompt

Request 3:
    image 3 + prompt

...

Request 100:
    image 100 + prompt
```

It is NOT:

```text
Request 1:
    image 1 + prompt

Request 2:
    image 1 + previous response
    + image 2 + prompt

Request 3:
    image 1 + response 1
    + image 2 + response 2
    + image 3 + prompt
```

This keeps requests independent and avoids unnecessarily carrying context between pages.

---

# 36. Privacy

The textbook images are sent to the Gemini API for processing.

Do not put private or sensitive images into the `images/` directory unless you're comfortable sending them to the configured API service.

The generated HTML and PDF stay on your computer.

---

# 37. Complete workflow

The complete process is:

```text
1. Install Python
       ↓
2. Create virtual environment
       ↓
3. Activate virtual environment
       ↓
4. Install requirements
       ↓
5. Create Gemini API key
       ↓
6. Add API key to .env
       ↓
7. Put textbook photos in images/
       ↓
8. Run python process.py
       ↓
9. Gemini processes each image independently
       ↓
10. Results are cached in output/pages/
       ↓
11. HTML booklet is generated
       ↓
12. PDF booklet is generated
       ↓
13. Print the exercises
```

---

# 38. Quick reference

If everything is already installed, the only commands you normally need are:

### Activate

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

### Run

```bash
python process.py
```

### Deactivate

```bash
deactivate
```

### Start completely over

macOS/Linux:

```bash
rm -rf output
```

Windows:

```powershell
Remove-Item -Recurse -Force output
```

Then:

```bash
python process.py
```

---

# 39. Files at a glance

```text
process.py
    Main application.

requirements.txt
    Python dependencies.

.env
    Gemini API key.
    NEVER commit this file.

images/
    Original textbook photos.

output/pages/
    Cached Gemini results, one file per image.

output/clean_test_booklet.html
    Complete printable HTML booklet.

output/clean_test_booklet.pdf
    Complete PDF booklet.

README.md
    Project documentation.
```

```

```
