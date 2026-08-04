from extractor import Extractor
from merger import Merger



extractor = Extractor()
lines=extractor.extract_pdf("C:/Users/HP/Desktop/stage_DSI/data/raw/referentiel_onssa.pdf")

print("Avant fusion :", len(lines), "lignes")

merger = Merger()
merged_lines = merger.merge(lines)

print("Après fusion :", len(merged_lines), "lignes")

print()

for line in merged_lines:
    if line.page == 94:
        print(line)