from classifier import LineClassifier
from pdf_types import LineType


class DocumentFilter:

    def __init__(self):
        self.classifier = LineClassifier()
        self.in_catalogue = False

    def keep(self, line):

        if not self.in_catalogue:

            if self.classifier.classifier(line) == LineType.FAMILY:
                self.in_catalogue = True
                return [line]

            return []

        return [line]