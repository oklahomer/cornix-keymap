# Cornix keymap.  `keymap.py` is the source of truth; everything else is
# generated from it.  Standard library Python only -- no virtualenv, no deps.

PYTHON ?= python3
ARTIFACT = build/oklahomer.vil

.PHONY: all build render test check import clean help

all: build render test		## regenerate everything and run the tests

build:				## keymap.py -> build/oklahomer.vil
	$(PYTHON) gen_vil.py

render:				## build/oklahomer.vil -> docs/layers.md
	$(PYTHON) render.py $(ARTIFACT) > docs/layers.md

test:				## run the test suite
	$(PYTHON) -m unittest discover -s tests -t .

check: build render test		## fail if the committed artifacts are stale
	@git diff --exit-code -- build docs \
	  || (echo "ERROR: build/ or docs/ is stale -- commit the regenerated files"; exit 1)
	@echo "artifacts are up to date"

# Compare a layout exported from the Vial GUI against the committed artifact.
#   make import FILE=~/Downloads/whatever.vil
# Exits non-zero on any drift and prints the rows as keymap.py literals so the
# change can be applied to the source by hand.
import:
	@test -n "$(FILE)" || (echo "usage: make import FILE=path/to/export.vil"; exit 2)
	$(PYTHON) render.py $(ARTIFACT) --diff "$(FILE)" --emit

clean:				## remove generated files
	rm -f $(ARTIFACT) docs/layers.md

help:				## list targets
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'
