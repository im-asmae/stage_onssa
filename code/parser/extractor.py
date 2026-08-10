"""
Extraction des lignes d'un PDF.

Principe :
- on extrait tous les spans du PDF ;
- on regroupe les spans ayant le même y ;
- on trie les spans de gauche à droite ;
- on reconstruit une vraie ligne.
"""

import fitz
from pdf_types import Line

class Extractor:

    # tolérance verticale (points PDF)

    Y_TOLERANCE = 2.0

    def extract_pdf(self, pdf_path):

        all_lines = []

        with fitz.open(pdf_path) as doc:

            for page_number, page in enumerate(doc, start=1):
                all_lines.extend(
                    self.extract_page(page, page_number)
                )

        return all_lines

    def extract_page(self, page, page_number):

        page_dict = page.get_text("dict")

        spans = []

        # Extraction de tous les spans

        for block in page_dict["blocks"]:

            if "lines" not in block:
                continue

            for line in block["lines"]:

                for span in line["spans"]:

                    text = span["text"].strip()

                    if not text:
                        continue

                    bbox = span["bbox"]

                    spans.append({
                        "text": text,
                        "font": span["font"],
                        "size": span["size"],

                        "x": bbox[0],
                        "y": bbox[1],

                        "width": bbox[2] - bbox[0],
                        "height": bbox[3] - bbox[1],

                        "bold": "Bold" in span["font"],
                        "italic": "Italic" in span["font"]
                    })

        # ordre vertical
        spans.sort(key=lambda s: (s["y"], s["x"]))

        # Regroupement par y
        groups = []

        for span in spans:

            placed = False

            for group in groups:

                if abs(group["y"] - span["y"]) <= self.Y_TOLERANCE:

                    group["spans"].append(span)
                    placed = True
                    break

            if not placed:

                groups.append({
                    "y": span["y"],
                    "spans": [span]
                })

        # Construction des lignes
        lines = []

        groups.sort(key=lambda g: g["y"])

        for group in groups:

            group["spans"].sort(key=lambda s: s["x"])

            text = " | ".join(
                span["text"]
                for span in group["spans"]
            )

            first = group["spans"][0]

            lines.append(
                Line(
                    text=text,

                    font=first["font"],
                    size=first["size"],

                    page=page_number,

                    x=first["x"],
                    y=group["y"],

                    width=first["width"],
                    height=first["height"],

                    bold=first["bold"],
                    italic=first["italic"]
                )
            )

        return lines