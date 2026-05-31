---
name: custom-image-overlays
description: "Programmatically draw and overlay custom icons, retro LED dot-matrix displays, and graphics onto wallpapers or photos using Pillow."
platforms: [linux, macos, windows]
---

# Custom Image Overlays & Retro Displays

A class-level procedural skill for programmatically generating custom icons, decals, watermarks, and retro hardware displays (like scrolling LED dot-matrix panels), and cleanly overlaying them onto specific coordinates of an image using Python's Pillow (PIL) library.

## When to Use

- User wants to add custom visual branding or elements (icons, stylized shapes, text, logos) onto an existing image, mockup, or desktop wallpaper.
- User wants a retro, cyberpunk, or physical-looking hardware display (like an LED dot-matrix scroll) synthesized into a specific area.
- User provides a local file path (`file:///...`) that the cloud agent cannot directly read, requiring a self-contained local Python script to perform the manipulation on their behalf.

## Design Patterns

### 1. Robust Coordinates & Sizing
Always analyze image dimensions first using Pillow to determine exact pixel ratios. Avoid heavy computer vision packages like OpenCV (`cv2`) in headless sandboxes, as they frequently crash due to missing system display drivers or library dependencies (like `libGL.so.1`). Use Pillow exclusively for image loading, coordinate detection, and drawing:
```python
from PIL import Image
img = Image.open("image.png")
width, height = img.size
```

### 2. High-Fidelity LED Dot-Matrix Display Generation
To generate an extremely realistic, physical-looking scrolling LED panel display:
1. **Render Text to Mask:** Render the target text onto a small monochrome "binary" mask image using monospaced fonts (e.g., `DejaVuSansMono-Bold.ttf`) or clean sans-serif fonts at a small font size (e.g., 12 to 16 pixels).
2. **Determine Grid Coordinates:** Map each pixel of this small binary text image to a cell (typically 3x3 or 4x4 pixels) on the main high-resolution panel.
3. **Render Individual LED State:**
   - **Active LED (ON):** Draw a bright neon circle (`0, 255, 100`) at the core, and draw a slightly larger circle underneath with a lower opacity (e.g., `70` out of `255`) to simulate radial bloom and light glow.
   - **Inactive LED (OFF):** Draw a very dark, faint green/red circle (`8, 25, 10`). Real hardware displays show inactive LEDs under room lighting; rendering them faintly makes the panel look authentic rather than a simple text graphic.
4. **Draw Physical Casing:** Draw a dark rectangular backing plate with a thin border slightly wider than the grid to make it look like a physical panel casing.

### 3. Procedural Silhouette & Icon Drawing
To draw smooth icons programmatically:
- Construct the shape using Pillow’s `ImageDraw.ellipse()` and `ImageDraw.polygon()` at high resolution (e.g., 200x200 or 400x400) on a transparent canvas.
- Rotate or warp to match perspective angles.
- Resize down using `Resampling.LANCZOS` to anti-alias edges, and apply a very light Gaussian blur (e.g., `radius=1.0` or `1.5`) for natural integration.

## local Path Workaround Pattern
If a user references a local file path (e.g., `file:///home/user/Pictures/...` or `/Users/username/...`):
1. **Acknowledge Isolation:** Explain that the cloud sandbox cannot read files on their local hard drive.
2. **Provide the Code:** Immediately provide a beautifully structured, highly documented Python script containing the exact PIL rendering logic.
3. **Offer Direct Download:** Write the code to a file in the workspace and upload it to a public file host (like `tmpfiles.org` or similar), then provide a direct download link.
4. **Unquote URL Characters:** In the python script, ensure you cleanly unquote URL characters (such as replacing `%20` with spaces) for local filesystem paths.

## Pitfalls

- **Extreme Low Opacity:** Placing elements or reflections at $<10\%$ opacity often makes them completely invisible on standard monitor displays or gets crushed by image compression. Maintain at least $20\%$ to $35\%$ opacity for faint reflections to be clearly appreciated at a distance while preserving the "glassy" feel.
- **Font Paths:** Always use robust system fonts that exist on target platforms (e.g. `/usr/share/fonts/truetype/dejavu/` on Debian/Ubuntu/openSUSE). Fall back to Pillow's default font if they are missing.
- **Save Formats:** Always convert images to `"RGB"` when saving as `.jpg` or `.jpeg` to prevent crashes when outputting RGBA canvases. Keep `"RGBA"` for `.png` outputs.
