from parser.classifier import LineClassifier
from parser.extractor import Extractor

pdf = "C:/Users/HP/Desktop/stage_onssa/data/referentiel_onssa.pdf"


extractor = Extractor()
lines=extractor.extract_pdf(pdf)


classifier = LineClassifier()

for line in lines[945:1050]:
    print(
        line.text,
        "->",
        classifier.classifier(line)
    )