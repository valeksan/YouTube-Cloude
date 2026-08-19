VENV    = .venv
PYTHON  = $(VENV)/bin/python
PIP     = $(VENV)/bin/pip

.PHONY: help venv setup setup-dev run gui test test-fast build build-gui build-nuitka clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

setup: venv ## Create venv and install runtime dependencies
	$(PIP) install -e .

setup-dev: venv ## Create venv and install all dependencies (with pytest)
	$(PIP) install -e ".[dev]"

run: ## Run CLI — usage: make run CMD="encode input.bin output.mp4"
	$(PYTHON) -m youtube_cloude $(CMD)

gui: ## Launch the GUI
	$(PYTHON) -m youtube_cloude.gui

test: setup-dev ## Run test suite
	$(PYTHON) -m pytest tests/ -v --tb=short

test-fast: setup-dev ## Run tests (stop on first failure)
	$(PYTHON) -m pytest tests/ -v --tb=short -x

build: setup-dev ## Build CLI binary with PyInstaller
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

build-gui: setup-dev ## Build GUI app as standalone executable
	$(PIP) install pyinstaller
	$(VENV)/bin/pyinstaller --onefile --windowed --name youtube-cloude-gui \
		--hidden-import youtube_cloude \
		--hidden-import youtube_cloude.core \
		--hidden-import youtube_cloude.encoder \
		--hidden-import youtube_cloude.decoder \
		--hidden-import youtube_cloude.utils \
		--hidden-import youtube_cloude.gui \
		--hidden-import youtube_cloude.uploader \
		--hidden-import youtube_cloude.compress \
		--hidden-import tkinter \
		--hidden-import tkinter.ttk \
		--hidden-import tkinter.filedialog \
		--hidden-import tkinter.messagebox \
		--hidden-import tkinter.scrolledtext \
		src/youtube_cloude/gui.py
	@echo ""
	@echo "Binary: dist/youtube-cloude-gui"

build-nuitka: setup-dev ## Build standalone binary with Nuitka
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
