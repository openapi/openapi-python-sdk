#!make

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                             #
#      ____                               _                                   #
#     / __ \____  ___  ____  ____ _____  (_) ®                                #
#    / / / / __ \/ _ \/ __ \/ __ `/ __ \/ /                                   #
#   / /_/ / /_/ /  __/ / / / /_/ / /_/ / /                                    #
#   \____/ .___/\___/_/ /_/\__,_/ .___/_/                                     #
#       /_/                    /_/                                            #
#                                                                             #
#   The Largest Certified API Marketplace                                     #
#   Accelerate Digital Transformation • Simplify Processes • Lead Industry    #
#                                                                             #
#   ═══════════════════════════════════════════════════════════════════════   #
#                                                                             #
#   Project:        openapi-python-sdk                                        #
#   Author:         Michael Cuffaro (@maiku1008)                              #
#   Copyright:      (c) 2025 Openapi®. All rights reserved.                   #
#   License:        MIT                                                       #
#   Maintainer:     Francesco Bianco                                          #
#   Contact:        https://openapi.com/                                      #
#   Repository:     https://github.com/openapi-it/openapi-python-sdk/         #
#   Documentation:  https://console.openapi.com/                              #
#                                                                             #
#   ═══════════════════════════════════════════════════════════════════════   #
#                                                                             #
#   "Truth lies at the source of the stream."                                 #
#                                  — English Proverb                          #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

## =========
## Variables
## =========

export PATH := $(HOME)/.local/bin:$(PATH)
VERSION := $(shell grep '^version' pyproject.toml | head -1 | sed 's/.*"\(.*\)".*/\1/')

## ====================
## Development Commands
## ====================

dev-push:
	@git config credential.helper 'cache --timeout=3600'
	@git add .
	@git commit -m "$$(read -p 'Commit message: ' msg; echo $$msg)" || true
	@git push

## ==================
## Quality Assurance
## ==================

.PHONY: lint

lint:
	@echo "Running ruff linter..."
	@poetry run ruff check .

## ================
## Release Commands
## ================

.PHONY: setup build publish release

setup:
	@poetry --version > /dev/null 2>&1 || \
		(echo "Installing Poetry..." && curl -sSL https://install.python-poetry.org | python3 -)

build: setup
	@echo "Building version $(VERSION)..."
	@poetry build

publish: build
	@echo "Publishing version $(VERSION) to PyPI..."
	@poetry publish

release: publish
	@echo "Tagging release $(VERSION)..."
	@git tag -fa "$(VERSION)" -m "Release $(VERSION)"
	@git push origin --tags -f
	@echo "Released $(VERSION) successfully."