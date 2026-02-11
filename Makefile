# ChipClaw Makefile
# Convenience wrapper around dev.sh

.PHONY: help test test-unit lint install-deps upload upload-tests clean

help:
	@echo "ChipClaw Development Commands"
	@echo ""
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make lint          - Check Python syntax"
	@echo "  make install-deps  - Install Python dependencies"
	@echo "  make upload        - Upload files to ESP32 (requires MPREMOTE_DEVICE)"
	@echo "  make upload-tests  - Upload tests to ESP32"
	@echo "  make clean         - Clean temporary files"
	@echo ""

test:
	@./dev.sh test

test-unit:
	@./dev.sh test-unit

lint:
	@./dev.sh lint

install-deps:
	@./dev.sh install-deps

upload:
	@./dev.sh upload

upload-tests:
	@./dev.sh upload-tests

clean:
	@./dev.sh clean
