# University of Washington Accessibility Guidelines

## Accessibility Requirements

All work on this project must comply with the **University of Washington Digital Accessibility Policy (APS 9.0)** and align with the ADA Digital Accessibility Initiative.

### Technical Standards
Follow **WCAG 2.1 Level AA** as the minimum standard:

#### Color and Contrast
- **Text contrast ratio**: Minimum 4.5:1 for normal text, 3:1 for large text (18pt+/14pt+ bold)
- **Graphical elements**: 3:1 contrast ratio for UI components and graphics
- **Do not rely on color alone** to convey information
- **Test tool**: Use WebAIM Contrast Checker or browser DevTools

#### Keyboard Accessibility
- **All interactive elements** must be keyboard accessible
- **Visible focus indicators** required on all focusable elements
- **Logical tab order** following visual layout
- **No keyboard traps** - users must be able to navigate away

#### Screen Reader Support
- **Semantic HTML**: Use proper heading hierarchy (h1, h2, h3)
- **Alt text**: All images need descriptive alt text (decorative images: `alt=""`)
- **ARIA labels**: Use `role`, `aria-label`, `aria-live` appropriately
- **Link text**: Must be meaningful out of context (avoid "click here")

#### Structure and Navigation
- **Page language**: Include `lang` attribute on html element
- **Heading hierarchy**: Don't skip levels (h1 → h3 is wrong)
- **Landmarks**: Use semantic HTML5 elements or ARIA landmarks
- **Skip links**: Provide navigation shortcuts for long content

#### Media and Content
- **Text alternatives**: Provide for all non-text content
- **Captions**: Required for video/audio content
- **Transcript**: Provide for audio-only content
- **Animations**: Respect `prefers-reduced-motion` media query

### Current Slide Implementation
The `slides.html` file implements:
- ✅ Semantic HTML with proper roles and ARIA labels
- ✅ Keyboard navigation (arrow keys)
- ✅ Screen reader announcements (`aria-live`)
- ✅ Alt text on logos
- ✅ Large, readable font sizes
- ✅ Visible navigation controls

### Before Committing
When modifying slides or web content:
1. **Verify color contrast** using a contrast checker
2. **Test keyboard navigation** - Tab through all interactive elements
3. **Check with screen reader** if possible (NVDA, JAWS, VoiceOver)
4. **Validate HTML** - Ensure semantic structure
5. **Review ARIA usage** - Only use when semantic HTML isn't sufficient

### Resources
- [UW Digital Accessibility](https://www.washington.edu/accessibility/digital/)
- [WebAIM WCAG 2.1 Checklist](https://webaim.org/standards/wcag/checklist)
- [WAVE Browser Extension](https://wave.webaim.org/extension/) - Accessibility evaluation tool
- [axe DevTools](https://www.deque.com/axe/devtools/) - Browser accessibility testing

### Contact
For accessibility questions: digitalaccess@uw.edu
