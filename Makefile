.PHONY: all html pdf clean open copy pdfv1 pdfv2 clean-all full release

all: clean pdfv1 pdfv2 open

html: output/karim-valiev-cv.html

pdfv1: output/karim-valiev-cv-v1.pdf

pdfv2: output/karim-valiev-cv-v2.pdf

open: output/karim-valiev-cv-v2.pdf
	open output/karim-valiev-cv-v2.pdf

output/karim-valiev-cv.html: karim-valiev-cv.md
	mkdir -p output
	ln -s ../res output/res
	pandoc --from=markdown-citations karim-valiev-cv.md -s -t html -o output/karim-valiev-cv.html --css res/my-gh-style.css -V "include-before=<article class='markdown-body'>" -V "include-after=</article>" -M "pagetitle=Karim Valiev" -M "lang=en"

output/karim-valiev-cv-v1.pdf: output/karim-valiev-cv.html res/github-markdown-light.css res/my-gh-style.css res/NotoColorEmoji.ttf res/css-reset.css
	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --no-margins --no-pdf-header-footer --run-all-compositor-stages-before-draw --virtual-time-budget=10000 output/karim-valiev-cv.html --print-to-pdf=output/karim-valiev-cv-v1.pdf

output/karim-valiev-cv-v2.pdf: output/karim-valiev-cv.html res/github-markdown-light.css res/my-gh-style.css res/NotoColorEmoji.ttf res/css-reset.css venv
	mkdir -p tmp
	prince --tagged-pdf output/karim-valiev-cv.html -o tmp/prince.pdf
	./venv/bin/python3 cleanup_pdf.py tmp/prince.pdf tmp/cleaned_up.pdf >/dev/null
	./venv/bin/python3 patch_emoji_cmap.py tmp/cleaned_up.pdf output/karim-valiev-cv-v2.pdf

copy: output/karim-valiev-cv-v2.pdf
	cp -a output/karim-valiev-cv-v2.pdf karim-valiev-cv.pdf

clean:
	rm -f output/karim-valiev-cv.html output/karim-valiev-cv-v1.pdf output/karim-valiev-cv-v2.pdf tmp/prince.pdf tmp/NotoColorEmoji.ttx output/res tmp/cleaned_up.pdf
	rm -rf _site

clean-all: clean
	rm -rf venv

venv:
	python3.13 -m venv venv
	venv/bin/pip install -r requirements.txt

full: clean-all venv pdfv1 pdfv2 open

release: copy 
	rsync -avz --exclude /.git --exclude /old --filter="dir-merge,- .gitignore" ./ ../my-cv-public/
	echo "Checking for untracked/deleted files in ../my-cv-public/"	
	if git -C ../my-cv-public ls-files --others --exclude-standard --deleted | grep --color=always '.*'; then echo "ERROR: There are untracked or deleted files in ../my-cv-public/"; exit 1; fi
	git -C ../my-cv-public add -u .
	git -C ../my-cv-public diff --cached --stat --color



