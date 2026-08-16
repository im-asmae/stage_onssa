from parser.extractor import Extractor
from parser.parser import Parser
from parser.exporter import Exporter
from parser.document_filter import DocumentFilter

pdf = "C:/Users/HP/Desktop/stage_onssa/data/referentiel_onssa.pdf"

extractor = Extractor()
filter = DocumentFilter()
parser = Parser()

lines = extractor.extract_pdf(pdf)

filtered_lines = []

for line in lines:
    if filter.keep(line):
        filtered_lines.append(line)

families = parser.parse(filtered_lines)

# Export
exporter = Exporter()
document = exporter.export(families)

# Sauvegarde
exporter.save(document, "referentiel.json")

print("Export terminé.")