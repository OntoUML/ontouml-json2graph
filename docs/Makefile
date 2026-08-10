# Minimal makefile for Sphinx documentation

PYTHON       ?= python
SPHINXBUILD  ?= $(PYTHON) -m sphinx
SOURCEDIR    = .
BUILDDIR     = _build
SPHINXOPTS   ?= -W --keep-going -n

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
