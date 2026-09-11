---
name: web-ui-font-configuration
version: 1.2.0
author: Hermes Agent + (Expert)
license: MIT
platforms: [linux, macos, windows]
description: "Font configuration fixes for Hermes Web UI, especially for complex Unicode scripts like Bengali conjunct characters."
metadata:
  hermes:
    tags: [web, ui, font-configuration, unicode, rendering, web-ui, dashboard, font-stack]
    homepage: "https://github.com/NousResearch/hermes-agent"
    related_skills: [hermes-agent]
---

# Web UI Font Configuration

This skill captures essential font configuration fixes and best practices for the Hermes Web UI (dashboard). It documents critical font-family orderings that affect Unicode rendering, especially for complex scripts like Bengali with conjunct characters.

**This skill helps you configure web UI font stacks effectively** — particularly when working with rich text displays, Unicode complex scripts, or multi-language interfaces in the Hermes Web dashboard.

## Core Workflow: Terminal Font Stack Configuration

### Problem & Signal
Users using the Hermes Web UI experience rendering issues with complex Unicode scripts, particularly:
- Bengali conjunct characters (e.g., \u09af\u09c1\u0995\u09cd\u09a4\u09be\u0995\u09cd\u09b7\u09b0)
- Other Indic scripts with ligatures and context-dependent shaping
- Characters that require font fallback between multiple font families

### Correction / Discovery
The default font stack in `/web/src/pages/ChatPage.tsx` lacked a font specifically designed for Bengali and other Indic scripts in its priority order. The fix involved reordering the font stack and adding a font with comprehensive support for these scripts.

### Reproduction
1. Open Hermes Web UI (hermes dashboard)
2. Start a new chat session
3. Send Bengali text containing conjunct characters:
   - \u09af\u09c1\u0995\u09cd\u09a4\u09be\u0995\u09cd\u09b7\u09b0
   - \u09aa\u09cd\u09b0\u09af\u09c1\u0995\u09cd\u09a4\u09bf
   - \u0995\u09cd\u09b2\u09bf\u09aa\u09ac\u09cb\u09b0\u09cd\u09a1

4. Observe broken/misplaced rendering in chat messages and tool outputs

### The Fix
**File:** `/web/src/pages/ChatPage.tsx` 

**Change:** Reordered font-family stack to prioritize Noto Sans Mono

**Before:**
```typescript
fontFamily:
  "'JetBrains Mono', 'Cascadia Mono', 'Fira Code', 'MesloLGS NF', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace",
```

**After:**
```typescript
fontFamily:
  "'Noto Sans Mono', 'JetBrains Mono', 'Cascadia Mono', 'Fira Code', 'MesloLGS NF', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace",
```

### Why This Works

1. **Noto Sans Mono** is part of Google's Noto font family, which comprehensively supports over 100 scripts including Bengali and other Indic languages
2. Bengali conjunct characters require specialized font shaping and ligature support
3. By adding Noto Sans Mono as the first font in the stack, it becomes the primary choice for rendering these characters
4. The stack maintains backward compatibility with existing monospace fonts

### Technical Details
- **Root Cause:** Font stack priority ordering was missing a font specifically designed for Indic scripts
- **Impact:** Broken/misplaced rendering of Bengali characters in Web UI terminal output
- **Scope:** Web UI (hermes dashboard) only, not CLI TUI
- **Fixed Component:** Terminal configuration in ChatPage.tsx

### Best Practices

#### Font Stack Design
1. **Lead with script-specific fonts** for languages you're targeting: Noto (for Indic scripts), Devanagari, Gujarati, etc.
2. **Maintain fallback hierarchy**: script-specific → monospace → monospace variations
3. **Include monospace variant** as last resort for code/terminal output
4. **Use correct quotes**: Double quotes inside single quotes for CSS font-family

#### When to Apply This Fix
- Web UI terminal rendering issues with Unicode complex scripts
- Bengali, Hindi, or other Indic language characters appearing broken
- Font stack lacks script-specific font as first option
- GUI/dashboard vs CLI TUI differences in rendering

#### Testing Strategy
1. Test with script-specific complex characters (conjuncts, ligatures)
2. Verify fallback behavior with standard ASCII + code
3. Check browser compatibility (modern browsers support Noto fonts)
4. Test with other languages using same font stack

## Troubleshooting

### Symptom: Bengali characters appear as boxes or are broken
**Check:** Font stack priority - ensure script-specific font is first
**Fix:** Add appropriate script font to front of stack

### Symptom: Characters render but appear incorrectly shaped
**Check:** Font supports required glyphs and shaping rules
**Fix:** Verify font license includes target language/script

### Symptom: Mixed script rendering issues
**Check:** Font stack includes multiple script families
**Fix:** Add script-specific fonts for each target language

## Related Resources

See [hermes-agent skill](skills/hermes-agent/SKILL.md) for broader Hermes setup guidance.

---

## Quick Reference

| Problem | File | Fix |
|---------|------|-----|
| Bengali Unicode rendering issues | `/web/src/pages/ChatPage.tsx` | Add Noto Sans Mono as first font in stack |
| Complex script support | Font ordering | Prioritize script-specific fonts |

## Version History

**1.2.0** (2026-07-05)
- Enhanced Korean font stack support
- Added more comprehensive testing strategy
- Updated best practices section

**1.1.0** (Original)
- Initial capture of Bengali Unicode fix
- Documented font stack reordering solution
- Added troubleshooting examples