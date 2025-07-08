# Autotranslator

A Python tool for automatic translation.

## Installation

This project uses uv for dependency management and virtual environments.

```bash
# Install uv if you don't have it
curl -sSf https://astral.sh/uv/install.sh | sh

# Create a virtual environment and install dependencies
uv venv
uv pip install -e .
```

## Usage

```bash
python main.py
```

## Development

This project uses ruff for style checking:

```bash
# Install dev dependencies
uv pip install ruff

# Run ruff
ruff check .
```
