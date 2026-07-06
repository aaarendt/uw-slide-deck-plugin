#!/bin/bash
# Wrapper script for rendering UW slides

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DECK_DIR="${1:-.}"

# Use the pixi environment to run the renderer
"${PLUGIN_DIR}/.pixi/envs/default/bin/python" "${PLUGIN_DIR}/render_slides.py" "${DECK_DIR}"
