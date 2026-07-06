When this skill is invoked:

1. Check that the current directory has a `content/` subdirectory with markdown files
2. Run the renderer script: `~/.claude/skills/uw-slides/skills/slide-renderer/render.sh .`
3. Report the output location and provide instructions for viewing

Example response:
```
I'll render your UW presentation now.

[Run the render.sh script]

✓ Presentation rendered successfully!
  Output: /path/to/your-deck/build/index.html
  Slides: 4

To view:
- Open build/index.html in your browser
- Use arrow keys or spacebar to navigate
- Click anywhere to advance slides
```

If errors occur, check:
- Is there a `content/` directory?
- Is pixi installed in the plugin? (First-time users need to run `pixi install`)
- Are the markdown files valid with proper frontmatter?
