# MES Chart Pack Generator - Simplified Workflow Makefile
# Separates data processing from chart generation

# Variables
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Date range variables (can be overridden) - aligned with sample data
START ?= 2019-05-06
END ?= 2019-05-12

# Default target
.DEFAULT_GOAL := help

## Setup and Installation
install: ## Install dependencies and setup virtual environment
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Installation complete! Use 'make sample' to test."

## Quick Testing
sample: ## Quick sample (1 week): process data + generate charts
	$(PYTHON) main.py --mode sample
	@echo "📄 Sample complete! Check samples/sample_pages.pdf"

## Production Workflow
data: ## Process data for date range (usage: make data START=2024-02-01 END=2024-02-07)
	$(PYTHON) main.py --mode data --start-date $(START) --end-date $(END)
	@echo "💾 Data processing complete for $(START) to $(END)"

charts: ## Generate charts from cached data (usage: make charts START=2024-02-01 END=2024-02-07) 
	$(PYTHON) main.py --mode charts --start-date $(START) --end-date $(END)
	@echo "📚 Charts generated for $(START) to $(END)"

## Main Workflow  
generate: ## Process data and generate charts (usage: make generate START=2019-05-06 END=2019-05-10)
	$(MAKE) data START=$(START) END=$(END)
	$(MAKE) charts START=$(START) END=$(END)
	@echo "✅ Complete workflow finished for $(START) to $(END)"

## Utility Commands
clean: ## Clean generated files and cache
	rm -f samples/*.pdf
	rm -f output/*.pdf
	rm -rf src/__pycache__
	rm -rf src/providers/__pycache__
	@echo "🧹 Cleaned generated files"

clean-data: ## Clean cached data files
	rm -f data/*.csv
	rm -f data/*_summary.txt
	@echo "🗑️ Cleaned data cache"

clean-all: clean clean-data ## Clean everything including data cache

## Development Commands
no-cache: ## Process data without cache (usage: make no-cache START=2024-02-01 END=2024-02-07)
	$(PYTHON) main.py --mode data --start-date $(START) --end-date $(END) --no-cache

lint: ## Check for unused imports and basic issues
	@echo "🔍 Checking for unused code..."
	@find src -name "*.py" -exec python3 -m py_compile {} \;
	@echo "✅ Basic syntax check passed"

info: ## Show system information
	@echo "📊 MES Chart Pack Generator - Simplified Workflow"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Dependencies: $$($(PIP) list --format=freeze | wc -l) packages installed"
	@echo "Data files: $$(ls -1 data/*.csv 2>/dev/null | wc -l) cached"
	@echo "Generated PDFs: $$(ls -1 *.pdf samples/*.pdf 2>/dev/null | wc -l) files"

## Maintenance Commands
reinstall: clean-all ## Reinstall everything from scratch
	rm -rf $(VENV)
	$(MAKE) install

update: ## Update dependencies
	$(PIP) install --upgrade -r requirements.txt

## Help
help: ## Show this help message
	@echo "🔥 MES Chart Pack Generator - Simplified Workflow:"
	@echo ""
	@echo "  \033[32m## Quick Testing:\033[0m"
	@awk 'BEGIN {FS = ":.*##"} /^sample:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "  \033[32m## Production Workflow:\033[0m"
	@awk 'BEGIN {FS = ":.*##"} /^(data|charts):.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "  \033[32m## Main Workflow:\033[0m"
	@awk 'BEGIN {FS = ":.*##"} /^generate:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "  \033[32m## Maintenance:\033[0m"
	@awk 'BEGIN {FS = ":.*##"} /^(install|clean|clean-data|clean-all|info|reinstall|update):.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "📖 Workflow Examples:"
	@echo "  make sample                                    # Quick 1-week test"
	@echo "  make generate START=2019-05-06 END=2019-05-10 # Process data + generate charts"
	@echo "  make data START=2019-05-06 END=2019-05-10     # Process data only (optional)"
	@echo "  make charts START=2019-05-06 END=2019-05-10   # Generate charts only (optional)"
	@echo ""

.PHONY: install sample generate data charts clean clean-data clean-all no-cache lint info reinstall update help