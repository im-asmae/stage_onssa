from extractor import Extractor
from merger import Merger
from document_filter import DocumentFilter
from parser import Parser
from chunk_builder import ChunkBuilder
from chunk_exporter import ChunkExporter


# Extraction
extractor = Extractor()
lines = extractor.extract_pdf(
    "C:/Users/HP/Desktop/stage_DSI/data/raw/referentiel_onssa.pdf"
)

# Fusion
merger = Merger()
lines = merger.merge(lines)

# Filtrage
filter = DocumentFilter()
lines = [line for line in lines if filter.keep(line)]

# Parsing
parser = Parser()
families = parser.parse(lines)

# Chunking
builder = ChunkBuilder()
chunks = builder.build(families)

print("Nombre de chunks :", len(chunks))

exporter = ChunkExporter()
exporter.export(chunks, "chunks.json")

print(f"{len(chunks)} chunks exportés.")

#print()
#print(chunks[0].text)
#print("="*80)
#print(chunks[30].text)
#print("="*80)
#print(chunks[-1].text)
