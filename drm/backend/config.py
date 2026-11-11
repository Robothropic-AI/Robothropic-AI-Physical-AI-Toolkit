"""Single place for model settings, so changing the model is a one-line edit.

Override without touching code via environment variables (PowerShell):
    $env:DRM_MODEL = "claude-sonnet-5-5"
    $env:DRM_EFFORT = "medium"
The API key is read from ANTHROPIC_API_KEY by the Anthropic SDK; never commit it.
"""
import os

MODEL = os.getenv("DRM_MODEL", "claude-sonnet-5-5")
EFFORT = os.getenv("DRM_EFFORT", "medium")  # low | medium | high ...



