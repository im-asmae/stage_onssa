from classifier import LineClassifier
from pdf_types import LineType
from models import Family, Culture, Section, Entry


class Parser:
    """
    Transforme une suite de lignes classifiées
    en objets métiers (Family, Culture, Section, Entry).
    """

    def __init__(self):

        self.classifier = LineClassifier()

        # Résultat final
        self.families = []

        # Etat courant du parser
        self.current_family = None
        self.current_culture = None
        self.current_section = None


    def parse(self, lines):
        """
        Parse toutes les lignes du document.
        """

        for line in lines:
            self.parse_line(line)

        return self.families


    def parse_line(self, line):
        """
        Analyse une ligne puis appelle
        le bon traitement.
        """

        line_type = self.classifier.classifier(line)

        if line_type == LineType.PAGE:
            return

        if line_type == LineType.UNKNOWN:
            return

        if line_type == LineType.FAMILY:
            self._handle_family(line)

        elif line_type == LineType.CULTURE:
            self._handle_culture(line)

        elif line_type == LineType.SECTION:
            self._handle_section(line)

        elif line_type == LineType.ENTRY:
            self._handle_entry(line)


    def _handle_family(self, line):

        family = Family(
            nom=line.text,
            page=line.page
        )

        self.families.append(family)

        self.current_family = family
        self.current_culture = None
        self.current_section = None


    def _handle_culture(self, line):

        if self.current_family is None:
            raise ValueError(
                f"Page {line.page} : culture sans famille ({line.text})"
            )

        culture = Culture(
            nom=line.text,
            page=line.page
        )

        self.current_family.add_culture(culture)

        self.current_culture = culture
        self.current_section = None


    def _handle_section(self, line):

        if self.current_culture is None:
            raise ValueError(
                f"Page {line.page} : section sans culture ({line.text})"
            )

        section = Section(
            nom=line.text,
            page=line.page
        )

        self.current_culture.add_section(section)

        self.current_section = section


    def _handle_entry(self, line):

        if self.current_section is None:

            self.current_section = Section(
                nom="__NO_SECTION__",
                page=line.page
            )

            if self.current_culture is None:
                raise ValueError(
                    f"Page {line.page} : entrée sans culture ({line.text})"
                )

            self.current_culture.add_section(self.current_section)

        entry = Entry(
            text=line.text,
            page=line.page
        )

        self.current_section.add_entry(entry)


    def get_result(self):
        return self.families