# Presentation Title

Brief description of your presentation goes here.

Target audience: 
Duration: 

## 01-title

Title slide with UW branding.
- Presenter name
- Title/affiliation
- Date

## 02-example

Add your slide ideas here. Use any format that makes sense to you:
- Bullet points
- Prose descriptions
- Notes to yourself
- Key messages

The LLM will read these notes when generating the HTML slides.

---

## Notes

To add a new slide:
1. Add a `## slide-id` heading in the order you want
2. Add your content notes under that heading
3. Ask your LLM to generate the slide based on SLIDES.md
4. Run `./build.sh` to build the presentation

To reorder slides:
1. Move the `## slide-id` headings around in this file
2. Run `./build.sh` to rebuild
