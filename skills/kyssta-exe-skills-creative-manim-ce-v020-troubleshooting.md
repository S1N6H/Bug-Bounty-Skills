---
name: manim-ce-v020-troubleshooting
description: "Manim CE v0.20+ breaking changes, common errors, and fixes — supplement to manim-video skill"
version: 1.0.0
platforms: [linux, macos, windows]
tags: [manim, animation, troubleshooting, v0.20, breaking-changes]
related_skills: [manim-video]
---

# Manim CE v0.20+ Troubleshooting & Breaking Changes

This skill captures session-specific findings when working with Manim CE v0.20+. It supplements the bundled `manim-video` skill with real-world error patterns and fixes discovered during production use.

## When to Use

- You're getting `TypeError` on `Rotating`, `VGroup`, `Text`, or animation signatures
- Animations aren't rendering or mobjects aren't appearing
- LaTeX/MathTex errors with raw strings
- Migration from Manim CE v0.19 or earlier

---

## Breaking Changes (v0.19 → v0.20+)

### 1. Rotating Animation Signature

```python
# WRONG (v0.19 style):
Rotating(mob, radians=TAU, about_point=center)

# RIGHT (v0.20+):
Rotating(mob, TAU, about_point=center)
# Second positional arg = radians; no 'radians=' keyword
```

**Error if wrong:** `TypeError: Animation.__init__() got an unexpected keyword argument 'radians'`

---

### 2. VGroup Type Enforcement

`VGroup` now strictly accepts only `VMobject` subclasses.

```python
# WRONG: Text is Mobject, not VMobject
group = VGroup(circle, Text("Label"))  # TypeError

# RIGHT: Use Group for mixed types
group = Group(circle, Text("Label"))

# RIGHT: VGroup fine for shapes-only or MathTex-only
shapes = VGroup(circle, square)
equations = VGroup(MathTex(r"a"), MathTex(r"b"))
```

**Error:** `TypeError: Only values of type VMobject can be added as submobjects of VGroup`

---

### 3. FadeOut Cleanup Pattern

Always use `Group(*self.mobjects)` for scene cleanup — handles mixed types safely.

```python
# RIGHT:
self.play(FadeOut(Group(*self.mobjects)))

# WRONG (fails if any Text in scene):
self.play(FadeOut(VGroup(*self.mobjects)))
```

---

### 4. Text letter_spacing Removed

```python
# WRONG:
Text("HERMES", letter_spacing=6)

# RIGHT: Use MarkupText with Pango attributes
MarkupText('<span letter_spacing="6000">HERMES</span>', font_size=18)
# Pango letter_spacing = 1/1024 of a point
```

---

### 5. Group.save_state() Not Implemented

```python
# WRONG:
group = Group(circle, Text("label"))
group.save_state()  # NotImplementedError!

# RIGHT: Use FadeIn with shift/scale
self.play(FadeIn(group, shift=UP * 0.3, scale=0.8))

# OR save/restore on individual VMobjects only
circle.save_state()
self.play(circle.animate.shift(RIGHT))
self.play(Restore(circle))
```

---

## Common Animation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Invisible animation | Mobject never added to scene | `self.play(Create(mob))` before animating |
| Transform leaves old | `Transform(A, B)` keeps A | Use `ReplacementTransform(A, B)` |
| Duplicate animation | Same mob twice in one `play()` | Chain: `mob.animate.shift().set_color()` |
| Updater conflicts | Updater fights animation | `mob.suspend_updating()` / `resume_updating()` |

---

## LaTeX / MathTex Pitfalls

| Pitfall | Fix |
|---------|-----|
| `MathTex("\frac{1}{2}")` | Use raw string: `MathTex(r"\frac{1}{2}")` |
| Unbalanced braces | Count braces: `r"\frac{1}{2}"` |
| Missing pdflatex | Install `texlive-full` (Linux) / `mactex` (macOS) |
| Missing package | Add to `TexTemplate().add_to_preamble(r"\usepackage{...}")` |

---

## Performance & Debugging

```bash
# Quick still for layout check
manim -ql -s script.py SceneName

# Disable caching when debugging
manim -ql --disable_caching script.py SceneName

# Production render
manim -qh script.py Scene1 Scene2 ...

# Stitch scenes
cat > concat.txt << 'EOF'
file 'media/videos/script/480p15/Scene1.mp4'
file 'media/videos/script/480p15/Scene2.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
```

**Frame timing:** `-ql` = 15fps → minimum `wait(0.067)` per frame. `wait(0.05)` auto-rounded up with warning.

---

## Session Artifact: Hermes Explainer Video

This session produced a 72-second Hermes Agent explainer using the `manim-video` skill (CPU-only, no GPU). Key patterns validated:

- 7 scenes, Build-Up arc architecture
- Shared color constants at file top (`BG`, `PRIMARY`, `SECONDARY`, `ACCENT`, `DIM`)
- Monospace font throughout (`font=MONO`)
- Subcaptions on every scene via `self.add_subcaption()`
- `Group(*self.mobjects)` cleanup pattern
- `Rotating(mob, TAU, about_point=center)` for orbit animation
- Draft at 480p15 (`-ql`), stitched via ffmpeg concat

Project structure used:
```
/root/hermes_video/
  plan.md          # Narrative, palette, scene breakdown
  script.py        # All 7 scene classes
  concat.txt       # ffmpeg scene list
  hermes_agent_explainer.mp4  # Final output
```

---

## References

- Bundled skill: `manim-video` (core pipeline, creative standards, references/)
- Manim CE changelog: https://github.com/ManimCommunity/manim/releases
- Manim CE docs: https://docs.manim.community/