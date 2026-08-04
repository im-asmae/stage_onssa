"""
Le rôle du Merger est de reconstruire les lignes logiques du document.

Il reçoit les objets Line produits par l'Extractor
et fusionne les lignes ayant la même coordonnée Y.
"""

from collections import defaultdict
from pdf_types import Line

class Merger:
    def merge(self, lines):

        #regrouper les lines par page
        pages=defaultdict(list)

        for line in lines:
            pages[line.page].append(line)
        
        #c'est ici qu'on mettra le résultat final
        merged_lines = []

        #traiter chaque page indépendamment
        for page_number in sorted(pages):

            page_lines=self.merge_page(pages[page_number])

            merged_lines.extend(page_lines)
        
        return merged_lines
    
    def merge_page(self, lines):
        """
        fusionne les lignes d'une seule page
        """

        #trier en haut vers le bas
        lines.sort(key=lambda line: line.y)

        #regrouper les lignes ayant presque le même y
        groups = defaultdict(list)

        for line in lines:

            #on arrondit y pour éviter les petites différences
            y=round(line.y)

            groups[y].append(line)
        
        #cette liste contiendra les nouvelles lignes
        merged=[]

        for y in sorted(groups):
            merged.append(
                self.merge_group(groups[y])
            )
        
        return merged
    


    def merge_group(self, group):
        """
        Fusionne un groupe de lignes ayant le même Y.
        """

        # Trier de gauche à droite
        group.sort(key=lambda line: line.x)

        # Construire le texte
        text = " | ".join(
            line.text
            for line in group
        )

        first = group[0]

        return Line(
            text=text,
            font=first.font,
            size=first.size,
            page=first.page,
            x=first.x,
            y=first.y,
        )
