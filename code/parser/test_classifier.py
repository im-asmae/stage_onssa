from classifier import LineClassifier
from extractor import Extractor
from merger import Merger

pdf = "C:/Users/HP/Desktop/stage_onssa/data/raw/referentiel_onssa.pdf"


extractor = Extractor()
lines=extractor.extract_pdf(pdf)

merger = Merger()
lines=merger.merge(lines)

classifier = LineClassifier()

for line in lines[945:1050]:
    print(
        line.text,
        "->",
        classifier.classifier(line)
    )