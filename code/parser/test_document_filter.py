from extractor import Extractor
from merger import Merger
from document_filter import DocumentFilter

extractor = Extractor()
lines = extractor.extract_pdf("C:/Users/HP/Desktop/stage_DSI/data/raw/referentiel_onssa.pdf")

merger = Merger()
lines = merger.merge(lines)

for line in lines:
    if line.page in [5, 6]:
        print(
            f"Page {line.page:2} | {line.font:25} | {line.size:5.1f} | {line.text}"
        )

"""filter = DocumentFilter()

for line in lines:
    if filter.keep(line):
        print(
            f"Page {line.page:3} | "
            f"{line.font:<25} | "
            f"{line.size:>5} | "
            f"{line.text}"
        )
"""