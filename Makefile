SHELL := /bin/bash

PYTHON ?= python3
PIP ?= pip3
MESON ?= meson
NINJA ?= ninja

SUGAR_DIR := repos/sugar
TOOLKIT_GTK4_DIR := repos/sugar-toolkit-gtk4
CASILDA_DIR := repos/casilda

CASILDA_BUILD_DIR := $(CASILDA_DIR)/_build
CASILDA_SO := $(CASILDA_BUILD_DIR)/src/libcasilda.so

DEBUG_PORT ?= 5678

.PHONY: all setup run debug test lint format clean \
        build-casilda build-toolkit-gtk4 build-sugar

all: setup

setup: build-casilda build-toolkit-gtk4 build-sugar

build-casilda:
	@echo "=== Building Casilda (Wayland compositor widget) ==="
	@if [ ! -d "$(CASILDA_BUILD_DIR)" ]; then \
		$(MESON) setup $(CASILDA_BUILD_DIR) $(CASILDA_DIR); \
	fi
	$(NINJA) -C $(CASILDA_BUILD_DIR)

build-toolkit-gtk4:
	@echo "=== Installing sugar-toolkit-gtk4 ==="
	$(PIP) install -e $(TOOLKIT_GTK4_DIR)

build-sugar:
	@echo "=== Bootstrapping Sugar shell ==="
	cd $(SUGAR_DIR) && NOCONFIGURE=1 ./autogen.sh
	cd $(SUGAR_DIR) && ./configure --prefix=/usr
	$(MAKE) -C $(SUGAR_DIR)

run: build-casilda build-toolkit-gtk4
	@echo "=== Launching Sugar shell (windowed mode, no fullscreen) ==="
	SUGAR_NO_FULLSCREEN=1 \
	GI_TYPELIB_PATH="$${HOME}/.local/usr/local/lib/girepository-1.0:$${HOME}/.local/lib/girepository-1.0:/usr/lib/girepository-1.0:/usr/lib/x86_64-linux-gnu/girepository-1.0" \
	LD_LIBRARY_PATH="$${HOME}/.local/usr/local/lib:$${HOME}/.local/lib:/usr/lib/x86_64-linux-gnu" \
	PYTHONPATH="$(CURDIR)/$(SUGAR_DIR)/src:$(CURDIR)/$(TOOLKIT_GTK4_DIR)/src:$$PYTHONPATH" \
	PATH="$(CURDIR)/$(TOOLKIT_GTK4_DIR)/.venv/bin:$$PATH" \
	$(PYTHON) $(SUGAR_DIR)/src/jarabe/main.py

debug: build-casilda build-toolkit-gtk4
	@echo "=== Launching Sugar shell with debugpy on port $(DEBUG_PORT) ==="
	SUGAR_NO_FULLSCREEN=1 \
	PYTHONPATH="$(CURDIR)/$(SUGAR_DIR)/src:$(CURDIR)/$(TOOLKIT_GTK4_DIR)/src:$$PYTHONPATH" \
	PATH="$(CURDIR)/$(TOOLKIT_GTK4_DIR)/.venv/bin:$$PATH" \
	$(PYTHON) -m debugpy --listen 0.0.0.0:$(DEBUG_PORT) --wait-for-client \
	-c "\
import gi; \
gi.require_version('Gtk', '4.0'); \
from jarabe import main; \
import sys; \
sys.exit(main.main.__code__)" \
	|| true

test:
	$(PYTHON) -m pytest repos/sugar-toolkit-gtk4/tests/ repos/sugar/tests/

lint:
	$(PYTHON) -m ruff check repos/sugar-toolkit-gtk4/src/ repos/sugar/src/jarabe/
	$(PYTHON) -m mypy repos/sugar-toolkit-gtk4/src/ repos/sugar/src/jarabe/

format:
	$(PYTHON) -m ruff format repos/sugar-toolkit-gtk4/src/ repos/sugar/src/jarabe/
	$(PYTHON) -m ruff check --fix repos/sugar-toolkit-gtk4/src/ repos/sugar/src/jarabe/

clean:
	rm -rf $(CASILDA_BUILD_DIR)
	rm -rf $(TOOLKIT_GTK4_DIR)/build $(TOOLKIT_GTK4_DIR)/*.egg-info
	cd $(SUGAR_DIR) && test -f Makefile && $(MAKE) distclean || true
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
