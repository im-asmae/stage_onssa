"""
le but est simplement de vérifier que l'extracteur produit bien des objets Line
"""

from extractor import Extractor
from classifier import LineClassifier

extractor = Extractor()

lines=extractor.extract_pdf("C:/Users/HP/Desktop/stage_DSI/data/raw/referentiel_onssa.pdf")

print(f"Nombre de lignes: {len(lines)}")

for line in lines:
    print(line)

    if line.page==37:
        print(line.y, line.text)

