
# from classifier import LineClassifier
# from pdf_types import LineType


# class DocumentFilter:

#     CHAPTERS = {
#         "Cultures fruitières",
#         "Cultures légumières",
#         "Grandes cultures",
#         "Plantes aromatiques et médicinales (PAM)",
#         "Cultures ornementales",
#         "Cultures tropicales",
#         "Zones non cultivées",
#         "Traitements généraux",
#     }

#     def __init__(self):
#         self.in_summary = False
#         self.classifier = LineClassifier()
#         self.current_chapter = None
#         self.first_family=None
#         self.pending_family = None
#         self.in_catalogue=False

#     def keep(self, line):

#         if not self.in_catalogue:

#             if line.text == "Agrumes":
#                 self.in_catalogue = True
#                 return [line]



#         if line.text.strip() in self.CHAPTERS and not self.in_summary:
#             self.in_summary = True
#             self.pending_family = None
#             return []

#         if self.in_summary:

#             line_type = self.classifier.classifier(line)

#             if line_type == LineType.FAMILY:
#                 self.pending_family = line
#                 return []

#             if line_type == LineType.CULTURE:
#                 self.in_summary = False

#                 if self.pending_family is not None:
#                     return [self.pending_family, line]

#                 return [line]
            

#             return []

#         return [line]


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