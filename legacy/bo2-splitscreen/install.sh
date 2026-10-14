#!/usr/bin/env bash
# Install the Black Ops II (BLUS31011) split-screen survival pack into a
# Windows RPCS3 tree mounted under WSL (default: /mnt/c/Users/$USER/RPCS3).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
RPCS3_DIR="${RPCS3_DIR:-/mnt/c/Users/$(whoami)/RPCS3}"

if [[ ! -d "$RPCS3_DIR" ]]; then
  echo "RPCS3 dir not found: $RPCS3_DIR" >&2
  echo "Set RPCS3_DIR=/path/to/RPCS3" >&2
  exit 1
fi

mkdir -p "$RPCS3_DIR/patches" "$RPCS3_DIR/config" "$RPCS3_DIR/config/custom_configs"

cp "$ROOT/BLUS31011_patch.yml" "$RPCS3_DIR/patches/BLUS31011_patch.yml"
cp "$ROOT/patch_config.yml" "$RPCS3_DIR/config/patch_config.yml"

# Build custom config from current global + our overrides (python for YAML-ish merge of known keys)
BASE="$RPCS3_DIR/config/config.yml"
OUT="$RPCS3_DIR/config/custom_configs/config_BLUS31011.yml"
if [[ ! -f "$BASE" ]]; then
  echo "missing $BASE — open RPCS3 once to create it" >&2
  exit 1
fi
cp "$BASE" "$OUT"
# sed-apply the knobs (same as we validated live)
sed -i \
  -e 's/^  SPU Block Size:.*/  SPU Block Size: Safe/' \
  -e 's/^  Accurate SPU DMA:.*/  Accurate SPU DMA: true/' \
  -e 's/^  PPU Reservation Priority Over SPUs:.*/  PPU Reservation Priority Over SPUs: true/' \
  -e 's/^  Accurate Cache Line Stores:.*/  Accurate Cache Line Stores: true/' \
  -e 's/^  Accurate RSX reservation access:.*/  Accurate RSX reservation access: true/' \
  -e 's/^  Disable SPU GETLLAR Spin Optimization:.*/  Disable SPU GETLLAR Spin Optimization: true/' \
  -e 's/^  SPU Wake-Up Delay:.*/  SPU Wake-Up Delay: 20/' \
  -e 's/^  Max SPURS Threads:.*/  Max SPURS Threads: 4/' \
  -e 's/^  RSX FIFO Fetch Accuracy:.*/  RSX FIFO Fetch Accuracy: Atomic/' \
  -e 's/^  Accurate ZCULL stats:.*/  Accurate ZCULL stats: false/' \
  -e 's/^  Relaxed ZCULL Sync:.*/  Relaxed ZCULL Sync: true/' \
  -e 's/^  Frame limit:.*/  Frame limit: 30/' \
  -e 's/^  Resolution:.*/  Resolution: 1280x720/' \
  -e 's/^  Resolution Scale:.*/  Resolution Scale: 100/' \
  -e 's/^    Exclusive Fullscreen Mode:.*/    Exclusive Fullscreen Mode: Disable/' \
  -e 's/^  Start games in fullscreen mode:.*/  Start games in fullscreen mode: false/' \
  "$OUT"

echo "Installed BO2 split-screen pack into $RPCS3_DIR"
echo "  patches/BLUS31011_patch.yml"
echo "  config/patch_config.yml (Enabled: true)"
echo "  config/custom_configs/config_BLUS31011.yml"
echo "Reboot BO2 for patches/config to take effect."
echo "Verify: Manage → Game Patches → 'BO2 split-screen: disable hang-detect watchdog'"
