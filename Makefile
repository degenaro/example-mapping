# Get the absolute path of the directory containing this Makefile
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Variables - Trestle Tooling
REPO_URL := https://github.com/oscal-compass/compliance-trestle.git
BRANCH   := v4.mapping.bob
SRC_DIR  := /tmp/compliance-trestle_src
VENV     := $(ROOT_DIR)/.venv
BIN      := $(VENV)/bin
PYTHON   := $(BIN)/python3

# Variables - CSF Catalog Generation
SCRIPT     := python/cyber_catalog.py
DATA       := data/csf2.xlsx
OUTPUT_DIR := catalogs/NIST_CSF_v2.0

.PHONY: all setup clone develop validate trestle-transform generate-csf-catalog generate-csf-mapping clean

all: setup clone develop generate-csf-catalog generate-csf-mapping trestle-transform validate

# 1. Unified Environment Setup
setup:
	@if [ ! -d "$(VENV)" ]; then \
		echo "==> Creating virtual environment..."; \
		python3 -m venv $(VENV); \
		$(BIN)/pip install --upgrade pip setuptools wheel; \
		$(BIN)/pip install pandas openpyxl; \
		echo "==> Venv initialized with pandas, openpyxl, and trestle base requirements."; \
	else \
		echo "==> Virtual environment already exists at $(VENV)"; \
	fi
	@mkdir -p $(OUTPUT_DIR)

# 2. Trestle Tooling Targets
clone:
	@if [ ! -d "$(SRC_DIR)" ]; then \
		echo "==> Cloning branch $(BRANCH)..."; \
		git clone --branch $(BRANCH) $(REPO_URL) $(SRC_DIR); \
	fi

develop: setup
	@if [ ! -f "$(BIN)/trestle" ]; then \
		echo "==> Installing trestle from source..."; \
		$(BIN)/pip install -e $(SRC_DIR); \
		echo "==> Running internal development setup..."; \
		cd $(SRC_DIR) && PATH="$(BIN):$(PATH)" $(MAKE) develop; \
	else \
		echo "==> Trestle already installed in virtual environment"; \
	fi

validate:
	@echo "==> Validating Trestle workspace at $(ROOT_DIR)..."
	@if [ ! -f "$(BIN)/trestle" ]; then \
		echo "Error: trestle binary not found. Run 'make develop'."; \
		exit 1; \
	fi
	$(BIN)/trestle validate -a

# 3. Specific Transformation Targets
trestle-transform: validate
	@echo "==> Running CSV to OSCAL conversion via Trestle..."
	$(BIN)/trestle task csv-to-oscal-mc -c content/csf2-mc.config

# LABEL: Generate CSF Catalog
# This target runs your custom transformation script
generate-csf-catalog: setup
	@echo "==> Running custom CSF transformation: $(SCRIPT)..."
	$(PYTHON) $(SCRIPT)

# LABEL: Generate CSF to 800-53 Mapping
# This target generates a CSV mapping from CSF to NIST 800-53
generate-csf-mapping: setup
	@echo "==> Running CSF to 800-53 mapping transformation..."
	$(PYTHON) python/cyber_mapping.py

# 4. Clean up
clean:
	@echo "==> Cleaning up environment and source..."
	rm -rf $(VENV) $(SRC_DIR)
	find . -type d -name "__pycache__" -delete