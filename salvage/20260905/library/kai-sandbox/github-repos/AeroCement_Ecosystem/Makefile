.PHONY: build clean deploy

BUILD_DIR=build
MAIN=main/main.tex

all: build

build:
	mkdir -p $(BUILD_DIR)
	tectonic --outdir $(BUILD_DIR) $(MAIN) --keep-intermediates
	@echo "[SUCCESS] PDF generated: $(BUILD_DIR)/main.pdf"

clean:
	rm -rf $(BUILD_DIR) *.aux *.log *.out *.toc *.gz

deploy: build
	git add .
	git commit -m "Build update: $$(date)"
	git push origin main
