VENV    = .venv
PYTHON  = $(VENV)/bin/python
PIP     = $(VENV)/bin/pip

.PHONY: help venv install install-dev run gui test test-fast build build-nuitka clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv ## Install runtime dependencies
	$(PIP) install -e .

install-dev: venv ## Install with dev dependencies (pytest etc.)
	$(PIP) install -e ".[dev]"

run: ## Run CLI — usage: make run CMD="encode input.bin output.mp4"
	$(PYTHON) -m youtube_cloude $(CMD)

gui: ## Launch the GUI
	$(PYTHON) -m youtube_cloude.gui

test: install-dev ## Run test suite
	$(PYTHON) -m pytest tests/ -v --tb=short

test-fast: install-dev ## Run tests (stop on first failure)
	$(PYTHON) -m pytest tests/ -v --tb=short -x

build: install-dev ## Build standalone binary with PyInstaller
	$(PIP) install pyinstaller
	$(VENV)/bin/pyinstaller --onefile --name youtube-cloude \
		--hidden-import youtube_cloude \
		--hidden-import youtube_cloude.core \
		--hidden-import youtube_cloude.encoder \
		--hidden-import youtube_cloude.decoder \
		--hidden-import youtube_cloude.utils \
		--hidden-import youtube_cloude.gui \
		--hidden-import youtube_cloude.uploader \
		--hidden-import youtube_cloude.compress \
		src/youtube_cloude/__main__.py
	@echo ""
	@echo "Binary: dist/youtube-cloude"

build-nuitka: install-dev ## Build standalone binary with Nuitka
	$(PIP) install nuitka
	$(PYTHON) -m nuitka --standalone --onefile \
		--include-package=youtube_cloude \
		--output-filename=youtube-cloude \
		src/youtube_cloude/__main__.py
	@echo ""
	@echo "Binary: youtube-cloude"

clean: ## Remove build artifacts and venv
	rm -rf build/ dist/ *.spec
	rm -rf src/*.egg-info src/youtube_cloude.egg-info
	rm -rf $(VENV)
	rm -rf .pytest_cache/ tests/__pycache__/ src/youtube_cloude/__pycache__/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete 2>/dev/null || true
