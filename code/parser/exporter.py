"""
Transforme les objets métiers (Family, Culture, Section, Entry)
en une représentation JSON.

Le parser construit les objets en mémoire.
L'Exporter est chargé de les convertir en dictionnaires Python
qui pourront ensuite être sauvegardés en JSON.
"""

import json


class Exporter:

    def export(self, families):
        """
        Convertit toutes les familles du document
        en une liste de dictionnaires.
        """

        document = []

        for family in families:
            document.append(
                self.export_family(family)
            )

        return document
    
    def export_family(self, family):
        """
        Convertit une Family en dictionnaire.
        """

        return {
            "family": family.nom,
            "cultures": [
                self.export_culture(culture)
                for culture in family.cultures
            ]
        }

    def export_culture(self, culture):

        return {
            "culture": culture.nom,
            "sections": [
                self.export_section(section)
                for section in culture.sections
            ]
        }

    def export_section(self, section):

        return {
            "section": section.nom,
            "entries": [
                entry.text
                for entry in section.entries
            ]
        }

    def save(self, document, path):

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                document,
                f,
                ensure_ascii=False,
                indent=4
            )