#!/usr/bin/env python3
"""
UW Slides Renderer
Converts markdown slides to HTML presentation using Jinja2 templates
"""

import re
import sys
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown


class SlideRenderer:
    def __init__(self, deck_dir="."):
        self.deck_dir = Path(deck_dir).resolve()
        self.content_dir = self.deck_dir / "content"
        self.assets_dir = self.deck_dir / "assets"
        self.output_dir = self.deck_dir / "build"
        self.output_dir.mkdir(exist_ok=True)

        # Find the plugin directory (where templates are)
        self.plugin_dir = Path(__file__).parent
        self.templates_dir = self.plugin_dir / "design-systems" / "uw-brand" / "templates"
        self.css_file = self.plugin_dir / "design-systems" / "uw-brand" / "colors_and_type.css"

        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

        self.md = markdown.Markdown(extensions=['extra', 'nl2br'])

    def parse_frontmatter(self, content):
        """Extract YAML frontmatter from markdown"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
                body = match.group(2)
                return frontmatter or {}, body
            except yaml.YAMLError as e:
                print(f"Warning: YAML parse error: {e}")
                return {}, content
        return {}, content

    def split_columns(self, body):
        """Split content by ::left:: and ::right:: markers"""
        # Remove speaker notes first
        body = re.sub(r'::note::.*?(?=$|\n##|\n::|$)', '', body, flags=re.DOTALL)

        left_match = re.search(r'::left::(.*?)(?=::right::|##|$)', body, re.DOTALL)
        right_match = re.search(r'::right::(.*?)(?=##|::|$)', body, re.DOTALL)

        left = left_match.group(1).strip() if left_match else ""
        right = right_match.group(1).strip() if right_match else ""

        return left, right

    def extract_notes(self, body):
        """Extract speaker notes from body"""
        notes_match = re.search(r'::note::(.*?)(?=$|\n##|\n::|$)', body, re.DOTALL)
        if notes_match:
            notes = notes_match.group(1).strip()
            body = re.sub(r'::note::.*?(?=$|\n##|\n::|$)', '', body, flags=re.DOTALL)
            return notes, body
        return "", body

    def markdown_to_html(self, text):
        """Convert markdown to HTML"""
        # Reset the markdown converter
        self.md.reset()
        return self.md.convert(text)

    def render_title_slide(self, meta, body, slide_number):
        """Render title slide using template"""
        # Parse body for presenter info
        notes, body = self.extract_notes(body)
        lines = [line.strip() for line in body.strip().split('\n') if line.strip()]

        title = ""
        subtitle = ""
        presenter_lines = []

        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
            elif line.startswith('## '):
                subtitle = line[3:].strip()
            elif not line.startswith('#'):
                presenter_lines.append(line)

        presenter = "\n".join(presenter_lines) if presenter_lines else meta.get('presenter', '')

        template = self.jinja_env.get_template('title.html')
        return template.render(
            slide_number=slide_number,
            title=title or meta.get('title', ''),
            eyebrow=meta.get('eyebrow', ''),
            presenter=presenter,
            accent_bar=meta.get('accent_bar', 'top')
        )

    def render_default_slide(self, meta, body, slide_number):
        """Render default content slide"""
        notes, body = self.extract_notes(body)

        # Convert markdown to HTML
        content_html = self.markdown_to_html(body)

        # Basic default template (inline since default.html might not exist)
        return f"""
<section data-label="{slide_number} {meta.get('title', '')}"
         aria-label="Slide {slide_number}: {meta.get('title', '')}"
         class="slide slide-default theme-{meta.get('theme', 'light')}">
  <div class="accent-bar {meta.get('accent_bar', 'top')}"></div>
  <div class="slide-inner">
    {'<p class="eyebrow">' + meta.get('eyebrow', '') + '</p>' if meta.get('eyebrow') else ''}
    <h2>{meta.get('title', '')}</h2>
    <div class="content">
      {content_html}
    </div>
  </div>
</section>
"""

    def render_two_column_slide(self, meta, body, slide_number):
        """Render two-column layout using template"""
        notes, body = self.extract_notes(body)
        left, right = self.split_columns(body)

        left_html = self.markdown_to_html(left)
        right_html = self.markdown_to_html(right)

        template = self.jinja_env.get_template('two-column.html')
        return template.render(
            slide_number=slide_number,
            title=meta.get('title', ''),
            eyebrow=meta.get('eyebrow', ''),
            theme=meta.get('theme', 'light'),
            accent_bar=meta.get('accent_bar', 'top'),
            left_content=left_html,
            right_content=right_html
        )

    def render_comparison_slide(self, meta, body, slide_number):
        """Render comparison layout using template"""
        notes, body = self.extract_notes(body)
        left, right = self.split_columns(body)

        left_html = self.markdown_to_html(left)
        right_html = self.markdown_to_html(right)

        template = self.jinja_env.get_template('comparison.html')
        return template.render(
            slide_number=slide_number,
            title=meta.get('title', ''),
            eyebrow=meta.get('eyebrow', ''),
            left_label=meta.get('left_label', 'Before'),
            left_content=left_html,
            left_theme=meta.get('left_theme', 'purple'),
            right_label=meta.get('right_label', 'After'),
            right_content=right_html,
            right_theme=meta.get('right_theme', 'white'),
            divider_label=meta.get('divider_label', ''),
            accent_bar=meta.get('accent_bar', 'top')
        )

    def render_code_slide(self, meta, body, slide_number):
        """Render code slide using template"""
        notes, body = self.extract_notes(body)

        # Extract code block
        code_match = re.search(r'```(\w+)?\n(.*?)\n```', body, re.DOTALL)
        if code_match:
            language = code_match.group(1) or 'text'
            code = code_match.group(2)
            # Remove code block from body
            caption = re.sub(r'```.*?```', '', body, flags=re.DOTALL).strip()
        else:
            language = meta.get('language', 'text')
            code = body
            caption = ''

        template = self.jinja_env.get_template('code.html')
        return template.render(
            slide_number=slide_number,
            title=meta.get('title', ''),
            eyebrow=meta.get('eyebrow', ''),
            code=code,
            language=language,
            caption=caption,
            theme=meta.get('theme', 'dark'),
            accent_bar=meta.get('accent_bar', 'left')
        )

    def render_transition_slide(self, meta, body, slide_number):
        """Render transition slide using template"""
        template = self.jinja_env.get_template('transition.html')
        return template.render(
            slide_number=slide_number,
            section_number=meta.get('section_number', ''),
            section_label=meta.get('section_label', ''),
            title=meta.get('title', ''),
            subtitle=meta.get('subtitle', ''),
            theme=meta.get('theme', 'purple')
        )

    def render_image_bottom_slide(self, meta, body, slide_number):
        """Render image-bottom slide using template"""
        notes, body = self.extract_notes(body)

        # Extract image from markdown
        img_match = re.search(r'!\[(.*?)\]\((.*?)\)', body)
        if img_match:
            image_alt = img_match.group(1)
            image_src = img_match.group(2)
            # Remove image from body
            body_text = re.sub(r'!\[.*?\]\(.*?\)', '', body).strip()
        else:
            image_alt = meta.get('image_alt', '')
            image_src = meta.get('image_src', '')
            body_text = body

        body_html = self.markdown_to_html(body_text)

        template = self.jinja_env.get_template('image-bottom.html')
        return template.render(
            slide_number=slide_number,
            title=meta.get('title', ''),
            eyebrow=meta.get('eyebrow', ''),
            body=body_html,
            image_src=image_src,
            image_alt=image_alt,
            caption=meta.get('caption', ''),
            theme=meta.get('theme', 'light'),
            accent_bar=meta.get('accent_bar', 'top')
        )

    def render_slide(self, filepath, slide_number):
        """Render a single slide from markdown file"""
        content = filepath.read_text()
        meta, body = self.parse_frontmatter(content)

        layout = meta.get('layout', 'default')

        if layout == 'title':
            return self.render_title_slide(meta, body, slide_number)
        elif layout == 'two-column':
            return self.render_two_column_slide(meta, body, slide_number)
        elif layout == 'comparison':
            return self.render_comparison_slide(meta, body, slide_number)
        elif layout == 'code':
            return self.render_code_slide(meta, body, slide_number)
        elif layout == 'transition':
            return self.render_transition_slide(meta, body, slide_number)
        elif layout == 'image-bottom':
            return self.render_image_bottom_slide(meta, body, slide_number)
        else:
            return self.render_default_slide(meta, body, slide_number)

    def load_order(self):
        """Load slide order from order.txt"""
        order_file = self.deck_dir / "order.txt"
        if not order_file.exists():
            # Default to sorted filenames
            return sorted([f.name for f in self.content_dir.glob("*.md")])

        slides = []
        for line in order_file.read_text().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                slides.append(line)
        return slides

    def generate_html(self):
        """Generate complete HTML presentation"""
        if not self.content_dir.exists():
            print(f"Error: content directory not found at {self.content_dir}")
            return None

        slides_html = []
        slide_order = self.load_order()

        for i, slide_file in enumerate(slide_order, 1):
            filepath = self.content_dir / slide_file
            if filepath.exists():
                print(f"Rendering slide {i}: {slide_file}")
                try:
                    slide_html = self.render_slide(filepath, i)
                    slides_html.append(slide_html)
                except Exception as e:
                    print(f"Error rendering {slide_file}: {e}")
                    import traceback
                    traceback.print_exc()

        # Load CSS
        css_content = ""
        if self.css_file.exists():
            css_content = self.css_file.read_text()

        # Additional slide-specific CSS
        slide_css = """
        /* Base styles */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Open Sans', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #000;
        }

        /* Slide container */
        .slide {
            width: 1920px;
            height: 1080px;
            position: relative;
            display: none;
            flex-direction: column;
        }
        .slide.active {
            display: flex !important;
        }

        /* Accent bars */
        .accent-bar {
            position: absolute;
            background: var(--uw-spirit-gold, #ffc700);
            z-index: 10;
        }
        .accent-bar.top {
            top: 0; left: 0; right: 0;
            height: 8px;
        }
        .accent-bar.left {
            top: 0; left: 0; bottom: 0;
            width: 8px;
        }

        /* Title slide */
        .slide-title {
            background: var(--uw-spirit-purple, #4b2e83);
            color: white;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 80px;
        }
        .slide-title h1 {
            font-family: 'Encode Sans', sans-serif;
            font-size: 72px;
            font-weight: 900;
            margin-bottom: 24px;
            text-transform: uppercase;
        }
        .slide-title .subtitle {
            font-size: 36px;
            margin-bottom: 48px;
        }
        .slide-title .presenter {
            font-size: 28px;
            color: var(--uw-husky-gold-web, #e8e3d3);
            white-space: pre-line;
        }

        /* Default slide */
        .slide-default {
            padding: 80px;
        }
        .slide-default.theme-light {
            background: white;
            color: #1a1a1a;
        }
        .slide-default.theme-dark {
            background: var(--uw-spirit-purple, #4b2e83);
            color: white;
        }
        .slide-default .slide-inner {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        .slide-default .eyebrow {
            font-size: 24px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 16px;
            font-weight: 600;
        }
        .slide-default.theme-light .eyebrow {
            color: var(--uw-spirit-purple, #4b2e83);
        }
        .slide-default.theme-dark .eyebrow {
            color: var(--uw-spirit-gold, #ffc700);
        }
        .slide-default h2 {
            font-family: 'Encode Sans', sans-serif;
            font-size: 56px;
            font-weight: 800;
            margin-bottom: 40px;
        }
        .slide-default.theme-light h2 {
            color: var(--uw-spirit-purple, #4b2e83);
        }
        .slide-default .content {
            font-size: 32px;
            line-height: 1.6;
        }
        .slide-default .content p {
            margin-bottom: 20px;
        }
        .slide-default .content ul {
            margin: 20px 0;
            padding-left: 40px;
        }
        .slide-default .content li {
            margin: 15px 0;
        }
        .slide-default .content img {
            max-width: 100%;
            height: auto;
            margin: 30px 0;
            border-radius: 8px;
        }

        /* Two-column slide */
        .slide-two-column {
            padding: 80px;
        }
        .slide-two-column.theme-light {
            background: white;
            color: #1a1a1a;
        }
        .slide-two-column.theme-dark {
            background: var(--uw-spirit-purple, #4b2e83);
            color: white;
        }
        .slide-two-column .slide-inner {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        .slide-two-column h2 {
            font-family: 'Encode Sans', sans-serif;
            font-size: 56px;
            font-weight: 800;
            margin-bottom: 40px;
        }
        .slide-two-column.theme-light h2 {
            color: var(--uw-spirit-purple, #4b2e83);
        }
        .slide-two-column .columns {
            display: flex;
            gap: 60px;
            flex: 1;
        }
        .slide-two-column .column {
            flex: 1;
            font-size: 30px;
            line-height: 1.6;
        }
        .slide-two-column .column-divider {
            width: 4px;
            background: var(--uw-spirit-gold, #ffc700);
        }
        .slide-two-column .column h2 {
            font-size: 40px;
            margin-bottom: 24px;
        }
        .slide-two-column .column ul {
            padding-left: 40px;
        }
        .slide-two-column .column li {
            margin: 15px 0;
        }

        /* Slide counter */
        .slide-counter {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 18px;
            z-index: 1000;
        }
        """

        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UW Presentation</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
{css_content}
{slide_css}
    </style>
</head>
<body>
    {''.join(slides_html)}

    <div class="slide-counter">
        <span id="current-slide">1</span> / <span id="total-slides">{len(slides_html)}</span>
    </div>

    <script>
    // Slide navigation
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;

    function showSlide(n) {{
        slides.forEach(slide => slide.classList.remove('active'));
        currentSlide = Math.max(0, Math.min(n, totalSlides - 1));
        slides[currentSlide].classList.add('active');
        document.getElementById('current-slide').textContent = currentSlide + 1;
    }}

    document.addEventListener('keydown', (e) => {{
        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{
            e.preventDefault();
            showSlide(currentSlide + 1);
        }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
            e.preventDefault();
            showSlide(currentSlide - 1);
        }} else if (e.key === 'Home') {{
            e.preventDefault();
            showSlide(0);
        }} else if (e.key === 'End') {{
            e.preventDefault();
            showSlide(totalSlides - 1);
        }}
    }});

    // Click to advance
    document.addEventListener('click', (e) => {{
        if (!e.target.closest('.slide-counter')) {{
            showSlide(currentSlide + 1);
        }}
    }});

    // Initialize
    showSlide(0);
    document.getElementById('total-slides').textContent = totalSlides;
    </script>
</body>
</html>
"""

        output_file = self.output_dir / "index.html"
        output_file.write_text(full_html)
        print(f"\n✓ Presentation rendered successfully!")
        print(f"  Output: {output_file}")
        print(f"  Slides: {len(slides_html)}")
        print(f"\nOpen in browser: file://{output_file}")
        return output_file


def main():
    """Main entry point"""
    # Get deck directory from command line or use current directory
    deck_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    renderer = SlideRenderer(deck_dir)
    renderer.generate_html()


if __name__ == "__main__":
    main()
