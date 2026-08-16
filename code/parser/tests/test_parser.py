from parser.extractor import Extractor
from parser.document_filter import DocumentFilter
from parser.parser import Parser

extractor = Extractor()
filter = DocumentFilter()
parser = Parser()

pdf = "C:/Users/HP/Desktop/stage_onssa/data/referentiel_onssa.pdf"
lines = extractor.extract_pdf(pdf)

filtered_lines = []

for line in lines:
    filtered_lines.extend(filter.keep(line))

print("===== PREMIÈRES LIGNES =====")

for line in filtered_lines[:20]:
    print(
        line.page,
        parser.classifier.classifier(line).name,
        line.text
    )

# Le parser est appelé UNE SEULE FOIS
families = parser.parse(filtered_lines)

for family in families:
    for culture in family.cultures:
        names = [s.nom for s in culture.sections]
        if len(names) != len(set(names)):
            print("\nCulture avec sections dupliquées :")
            print("Famille :", family.nom)
            print("Culture :", culture.nom)
            print(names)
