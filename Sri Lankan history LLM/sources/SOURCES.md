# Source list

Drop the files below into this `sources/` folder, then run `python ingest.py` from the project root. The ingest script picks up `.pdf`, `.html`, `.htm`, `.txt`, and `.md` files automatically.

## Public-domain chronicles

- **Mahavamsa** (Wilhelm Geiger's English translation, 1912). The most-cited primary chronicle for the Anuradhapura period.
  - https://www.sacred-texts.com/bud/mhv/index.htm
  - Save the chapter pages as `.html` or copy into a single `.txt` file named `mahavamsa_geiger.txt`.

- **Culavamsa** (Geiger's English translation, two volumes, 1929). Continues the Mahavamsa from the late Anuradhapura period through the Polonnaruwa, Transitional, and Kandyan eras.
  - https://archive.org/details/culavamsabeingmo01geig (Volume I)
  - https://archive.org/details/culavamsabeingmo02geig (Volume II)
  - Download the PDF or full-text from archive.org.

- **Dipavamsa** (Hermann Oldenberg's edition, 1879). Older than the Mahavamsa, covers the same early period.
  - https://archive.org/details/dpavasaaance00oldegoog

## Wikipedia (cite as supplementary, not primary)

Save each as a single-page HTML file (Cmd+S → "Webpage, HTML only") into `sources/wiki/`.

- History of Sri Lanka: https://en.wikipedia.org/wiki/History_of_Sri_Lanka
- Anuradhapura Kingdom: https://en.wikipedia.org/wiki/Anuradhapura_Kingdom
- Polonnaruwa Kingdom: https://en.wikipedia.org/wiki/Kingdom_of_Polonnaruwa
- Kandyan Kingdom: https://en.wikipedia.org/wiki/Kingdom_of_Kandy
- Portuguese Ceylon: https://en.wikipedia.org/wiki/Portuguese_Ceylon
- Dutch Ceylon: https://en.wikipedia.org/wiki/Dutch_Ceylon
- British Ceylon: https://en.wikipedia.org/wiki/British_Ceylon
- Kandyan Convention: https://en.wikipedia.org/wiki/Kandyan_Convention
- Sri Lankan independence movement: https://en.wikipedia.org/wiki/Sri_Lankan_independence_movement
- Sri Lankan Civil War: https://en.wikipedia.org/wiki/Sri_Lankan_Civil_War

## Academic papers (open access)

- **JSTOR Open** — search "Sri Lanka history" on https://www.jstor.org/open/. Many archaeology and Mahavamsa-criticism papers are free.
- **Sri Lanka Journal of the Humanities** — open archive at https://sljh.sljol.info/
- **Journal of the Royal Asiatic Society of Sri Lanka** — older issues at https://www.jstor.org/journal/jroyaasiatsocs
- **Department of Archaeology, Sri Lanka** — annual reports and inscription publications: https://www.archaeology.gov.lk/
- **Epigraphia Zeylanica** (multi-volume corpus of Sri Lankan inscriptions): https://archive.org/details/epigraphiazeylan01rideuoft

Download the PDFs and drop them straight into `sources/`.

## Tips

- Bigger sources improve answer quality but slow ingest. Start with the chronicles and 5–10 Wikipedia articles, run the app, then add academic papers as you need depth.
- Rename files descriptively before ingesting — the file name is what the bot cites, so `mahavamsa_chapter_25_dutugemunu.txt` cites better than `page1.html`.
- For scanned PDFs (image-only), run OCR first (e.g. with `ocrmypdf`) so the text is extractable.
