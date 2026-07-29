# Shard Foundry // 16-bit Platform Module

**Status:** Runtime-integrated beta-production asset

The Foundry now uses one restrained industrial platform material across its
procedural collision platforms. Zone color remains as a low-opacity two-pixel
navigation accent; it no longer recolors the whole platform.

## Source and runtime

- Image-generation master:
  `Raw/foundry-platform-module-imagegen-v1.png`
- Chroma-keyed transparent master:
  `foundry-platform-module-transparent-v1.png`
- Shipping sprite:
  `Images/Game/Super-Frgmnts/foundry-platform-module-runtime-v1.png`
- Runtime size: `416 × 60`, RGBA
- Rendering: nearest-neighbor, scaled to the authored collision rectangle

## Generation record

Tool: OpenAI built-in image generation.

Prompt summary: one side-on, orthographic, seamless industrial catwalk module
in authentic 16-bit pixel art; desaturated blue-gray steel, charcoal recesses,
worn bronze hardware, and one muted amber indicator; isolated on a perfectly
flat `#00ff00` chroma-key background; no text, perspective, characters,
shadows, or background variation.

The chroma key was removed with the ImageGen skill helper. The alpha bounds
were cropped and reduced with nearest-neighbor sampling to produce the runtime
sprite. The generated master is preserved unchanged.
