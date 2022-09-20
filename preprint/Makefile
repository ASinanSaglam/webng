BUILD_DIR=build
# MAIN_FILE=main_old.md
MAIN_FILE=main.md

all: paper

paper:
	mkdir -p $(BUILD_DIR)
	cp -r ./*.md bibliography/* images/* $(BUILD_DIR)
	cd $(BUILD_DIR) && pandoc --standalone --citeproc \
	-f markdown+yaml_metadata_block+tex_math_dollars+raw_tex \
	--filter panflute -o main.tex $(MAIN_FILE)
	-cd $(BUILD_DIR) && pdflatex -interaction=nonstopmode main.tex &> /dev/null
	-cd $(BUILD_DIR) && bibtex main &> /dev/null
	-cd $(BUILD_DIR) && pdflatex -interaction=nonstopmode main.tex &> /dev/null
	-cd $(BUILD_DIR) && pdflatex -interaction=nonstopmode main.tex &> /dev/null
	cp $(BUILD_DIR)/main.pdf .

clean:
	rm -r build

.PHONY: all clean paper
