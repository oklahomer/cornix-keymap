# Architecture decision records

One decision per file. Read them in order the first time; after that, the keymap
source and the README link to the ones that explain a particular choice.

| # | Decision |
| --- | --- |
| [1](0001-ship-a-vil-on-the-stock-rmk-firmware.md) | Ship a `.vil` on the stock firmware |
| [2](0002-text-definition-is-the-source-of-truth.md) | A text definition is the source of truth, not the board |
| [3](0003-split-responsibility-between-firmware-and-karabiner.md) | Firmware settings and mapping-software settings have separate jobs |
| [4](0004-reproduce-dual-role-keys-with-firmware-mod-tap.md) | Dual-role keys are firmware mod-taps, tuned to decide on events not time |
| [5](0005-numbers-and-function-keys-live-on-the-home-rows.md) | Numbers and function keys live on the QWERTY row, reached by a layer |
| [6](0006-special-keys-belong-on-the-thumb-arc.md) | Special keys go on the thumb arc, and keep their old order |
| [7](0007-inner-column-moves-to-the-encoder-pushes.md) | The inner column moves to the encoder push-buttons |
| [8](0008-keep-paired-modifiers-distinct.md) | Left and right modifiers stay separate physical keys |
| [9](0009-drop-the-app-layer.md) | The application-launcher layer is removed |
| [10](0010-preserve-vendor-keycodes-and-untouched-layers.md) | Generate from the vendor export, and keep what it contains |
| [11](0011-verification-compares-it-does-not-regenerate.md) | Verification compares the artifacts, it does not regenerate them |
| [12](0012-pin-the-vendor-template-by-digest.md) | Pin the vendor template by digest |
