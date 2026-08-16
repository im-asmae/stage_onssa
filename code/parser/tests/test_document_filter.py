from parser.extractor import Extractor

extractor = Extractor()

lines = extractor.extract_pdf(
    "C:/Users/HP/Desktop/stage_onssa/data/referentiel_onssa.pdf"
)

for line in lines[:30]:
    print(
        f"{line.page} | "
        f"{line.text} | "
        f"size={line.size:.1f} | "
        f"bold={line.bold} | "
        f"italic={line.italic} | "
        f"font={line.font}"
    )