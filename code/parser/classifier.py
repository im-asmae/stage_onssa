"""
son but est : à partir d'une ligne extraite par PyMupdf , détermine son type
"""

from pdf_types import LineType, Line

class LineClassifier:
    # Constante de classe contenant la liste des sections connues
    SECTIONS = {
        "adventices",
        "ravageurs",
        "maladies",
        "divers",
        "traitement du sol",
    }


    def _approx_size(self, size: float, target: float, tolerance: float = 0.5) -> bool:
        """Vérifie si la taille de police est proche de la cible avec une tolérance."""
        return abs(size - target) <= tolerance

    def est_page(self, line: Line) -> bool:
        """
        Identifie les lignes de pagination ou d'en-tête technique.
        Exemples : 'Page 6', 'REF/CU/06/15/A'
        """
        return (
            line.text.startswith("Page")
            or line.text.startswith("REF/")
        )
    def est_famille(self, line: Line) -> bool:
        """Famille : Calibri Italic, taille ≈ 14."""
        return (
            "calibri" in line.font.lower()
        and "italic" in line.font.lower()
        and self._approx_size(line.size, 14)
        )

    def est_culture(self, line: Line) -> bool:
        """Culture : Times Italic, taille ≈ 14."""
        return (
            "times" in line.font.lower()
        and "italic" in line.font.lower()
        and self._approx_size(line.size, 14)
        )

    def est_section(self, line: Line) -> bool:
        """Section : Uniquement basée sur la présence du texte dans les sections connues."""
        return line.text.lower() in self.SECTIONS

    def est_entree(self, line: Line) -> bool:
        """Entrée : Calibri, taille ≈ 11, et n'est pas une Section."""
        if self.est_section(line):
            return False
        return (
        "calibri" in line.font.lower()
        and self._approx_size(line.size, 11)
    )
    def classifier(self, line: Line) -> LineType:
        """
        Détermine le type de la ligne.
        L'ordre des validations évite les conflits d'interprétation.
        """
        if self.est_page(line): return LineType.PAGE

        if self.est_section(line): return LineType.SECTION

        if self.est_famille(line): return LineType.FAMILY

        if self.est_culture(line): return LineType.CULTURE

        if self.est_entree(line): return LineType.ENTRY

        return LineType.UNKNOWN

