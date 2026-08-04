from extractor import Extractor
from merger import Merger
from parser import Parser
from exporter import Exporter
from document_filter import DocumentFilter

pdf = "C:/Users/HP/Desktop/stage_DSI/data/raw/referentiel_onssa.pdf"

extractor = Extractor()
merger = Merger()
filter = DocumentFilter()
parser = Parser()

lines = extractor.extract_pdf(pdf)
lines = merger.merge(lines)

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