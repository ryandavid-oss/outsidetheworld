# Dras Ehdre — Revision 3B

Status: review candidate. Nothing in this folder is integrated into the live
game or accepted as permanent production art.

## Identity authority

The identity authority is
`Raw/dras-identity-crop-v1.png`, selected from the user's original repeated
concept strip:

`/Users/rylee/Downloads/ChatGPT Image Jul 24, 2026 at 11_21_08 PM.png`

The selected pose preserves the complete staff, face, scarf, coat hem, gear,
boots, and three-quarter stance.

## Background extraction

The built-in image-generation editor was used in **background-extraction** mode
with the local identity crop as the only reference. The exact prompt is stored
in `dras-background-extraction-prompt-v1.txt`. It instructed the editor to change
only the studio background to a flat `#00ff00` chroma field.

The generated chroma image is `Raw/dras-chroma-v1.png`. Transparency was created
with the ImageGen skill's local `remove_chroma_key.py` helper:

```text
--auto-key corners
--soft-matte
--transparent-threshold 12
--opaque-threshold 220
--edge-contract 0
--edge-feather 0.35
--despill
```

The deterministic review builder then removes only alpha values below 8, crops
to the visible silhouette with 12 pixels of master padding, and creates the
runtime candidate.

## Runtime recommendation

- Transparent draw canvas: 96 × 112
- Visible Dras silhouette: 104 pixels high
- Plate-two local anchor: X 280
- Feet: world Y 744
- NPC collision: none in the blocking proposal

The scale study deliberately compares 96, 104, and 112 visible pixels beside
Aryn's actual 112 × 112 draw sprite. The 104-pixel option is recommended because
it preserves Dras's human scale while allowing his coat to feel substantial.

## Motion status

The idle/talk sheet is a motion contract, not accepted animation. It proposes a
continuous 1600ms rhythm, ±1 pixel of body travel, a planted staff, and very
restrained device-light breathing. Reduced motion uses the static rest pose.

## Rebuild

```sh
python3 tools/build_super_frgmnts_dras_review.py --prepare-identity
python3 tools/build_super_frgmnts_dras_review.py --build-reviews
```
