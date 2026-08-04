from extractor import Extractor
from merger import Merger
from document_filter import DocumentFilter
from parser import Parser

extractor = Extractor()
merger = Merger()
filter = DocumentFilter()
parser = Parser()

pdf = "C:/Users/HP/Desktop/stage_DSI/data/raw/referentiel_onssa.pdf"

lines = extractor.extract_pdf(pdf)
lines = merger.merge(lines)

filtered_lines = []

for line in lines:
    filtered_lines.extend(filter.keep(line))

print("\n===== LIGNES CONSERVÉES PAGES 5 ET 6 =====")

for line in filtered_lines:
    if 5 <= line.page <= 8:
        print(
            f"page={line.page:2} | "
            f"{parser.classifier.classifier(line).name:8} | "
            f"{line.text}"
        )
families = parser.parse(filtered_lines)

for family in families:
    print(f"\nFamille : {family.nom}")

    for culture in family.cultures:
        print(f"   Culture : {culture.nom}")