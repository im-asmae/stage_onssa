from parser.extractor import Extractor
from parser.document_filter import DocumentFilter
from parser.parser import Parser
from parser.chunk_builder import ChunkBuilder
from parser.chunk_exporter import ChunkExporter

pdf = "C:/Users/HP/Desktop/stage_onssa/data/referentiel_onssa.pdf"

extractor = Extractor()
filter = DocumentFilter()
parser = Parser()
builder = ChunkBuilder()
exporter = ChunkExporter()

# Pipeline
lines = extractor.extract_pdf(pdf)

filtered = []
for line in lines:
    filtered.extend(filter.keep(line))

families = parser.parse(filtered)

chunks = builder.build(families)

print(f"Nombre de chunks : {len(chunks)}")

print("\n===== PREMIERS CHUNKS =====")

for chunk in chunks[:3]:
    print("=" * 60)
    print("ID :", chunk.id)
    print("Metadata :", chunk.metadata)
    print(chunk.text[:400])   # affiche les 400 premiers caractères
    print()

exporter.export(chunks, "chunks.json")

print("\nExport terminé.")