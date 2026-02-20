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
CSF_CATALOG_SCRIPT  := python/cyber_catalog.py
CSF_MAPPING_SCRIPT  := python/cyber_mapping.py
CSF_DATA            := data/csf2.xlsx
CSF_OUTPUT_DIR      := catalogs/NIST_CSF_v2.0
CSF_CSV             := content/csf2_to_800-53_crosswalk.csv
CSF_MC_CONFIG       := content/csf2-mc.config

# Variables - NIST Mapping Generation
NIST_MAPPING_SCRIPT := python/nist_mapping.py
NIST_DATA           := data/sp800-53r4-to-r5-comparison-workbook.xlsx
NIST_CSV            := content/nist_rev5_to_nist_rev4_crosswalk.csv

.PHONY: all setup clone develop validate clean
.PHONY: csf csf-catalog csf-csv csf-json
.PHONY: nist nist-csv nist-json

all: setup clone develop csf nist

# ============================================================================
# COMMON: Environment Setup and Trestle Tooling
# ============================================================================

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
	@mkdir -p $(CSF_OUTPUT_DIR)
	@mkdir -p content

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

clean:
	@echo "==> Cleaning up environment and source..."
	rm -rf $(VENV) $(SRC_DIR)
	find . -type d -name "__pycache__" -delete

# ============================================================================
# CSF: Cybersecurity Framework Catalog and Mapping
# ============================================================================

csf: csf-catalog csf-csv csf-json
	@echo "==> CSF workflow complete: catalog, CSV, and JSON generated"

csf-catalog: setup
	@echo "==> Generating CSF catalog from Excel..."
	$(PYTHON) $(CSF_CATALOG_SCRIPT)

csf-csv: setup
	@echo "==> Generating CSF to 800-53 mapping CSV..."
	$(PYTHON) $(CSF_MAPPING_SCRIPT)

csf-json: csf-csv develop
	@echo "==> Converting CSF CSV to OSCAL JSON mapping collection..."
	$(BIN)/trestle task csv-to-oscal-mc -c $(CSF_MC_CONFIG)

# ============================================================================
# NIST: NIST SP 800-53 Rev 5 to Rev 4 Crosswalk
# ============================================================================

nist: nist-csv nist-json
	@echo "==> NIST workflow complete: relationships Excel, summary.md, CSV, and JSON generated"

nist-csv: setup
	@echo "==> Generating NIST Rev 5 to Rev 4 relationships, summary, and CSV..."
	$(PYTHON) $(NIST_MAPPING_SCRIPT)

nist-json: nist-csv develop
	@echo "==> Converting NIST CSV to OSCAL JSON mapping collection..."
	$(BIN)/trestle task csv-to-oscal-mc -c content/nist-mc.config