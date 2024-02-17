# regex to match recipe names and their comments:
# ^    (?P<recipe>\S+)(?P<args>(?:\s[^#\s]+)*)(?:\s+# (?P<docs>.+))*

# Constants
# [DO NOT MODIFY] src start
src := "whinesnips"
# src end

# Choose recipes
default:
    @ just -lu; printf '%s ' press Enter to continue; read; just --choose

[private]
[unix]
b64e file:
    base64 -w0 {{file}}

# Run Menu Commands
[private]
menu cmd:
    python -c "\"from dev.scripts.py.main import main;main('{{cmd}}')\""

# Run Without Time
[private]
menu_wt cmd:
    @ python -c "\"from dev.scripts.py.main import main;main('{{cmd}}')\""

[private]
nio_dev:
    @ python -m no_implicit_optional dev; exit 0

[private]
nio_src:
    @ python -m no_implicit_optional {{ src }}; exit 0

[private]
ruff:
    @ python -m ruff check dev/scripts/py --fix; python -m ruff check {{ src }} --fix; exit 0

# Set up development environment
bootstrap:
    #!/usr/bin/env bash
    rm -rf poetry.lock
    poetry install --with dev
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install mkdocs mkdocs-material mkdocs-minify-plugin mkdocs-redirects
    for i in $(ls -d dev/scripts/py/inst_mods/*/); do
        case $i in
            *"__pycache__"*) ;;
            *) python -m pip install -e "${i%%/}";;
        esac
    done

# Generate documentation
docs:
    just test
    just menu "docs"

# Get program's version
ver: (menu "ver")

# Set the version manually
set_ver: (menu "set_ver")

# Bump version
bump: (menu "bump")

# Push to Github
push: (menu "push")

# Generate Dynamic Files
gdf: (menu "gdf")

# Lint codebase
lint:
    @ just nio_dev
    @ just nio_src
    @ python -m mdformat docs
    @ python -m black -q .
    @ just ruff

# Test
test:
    python -m pytest --junitxml=tmp/junit.xml

# Build
build:
    rm -rf dist
    just gdf
    just docs
    just lint
    poetry build
