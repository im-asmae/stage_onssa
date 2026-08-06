from models import Chunk
import unicodedata


class ChunkBuilder:
    """
    Transforme les objets métiers (Family, Culture, Section...)
    en chunks destinés au RAG.
    """

    def build(self, families):

        chunks = []

        for family in families:
            for culture in family.cultures:
                for section in culture.sections:

                    chunk = self.build_chunk(
                        family,
                        culture,
                        section
                    )

                    chunks.append(chunk)

        return chunks


    @staticmethod
    def normalize(text):
        text = unicodedata.normalize("NFD", text)
        text = "".join(
            c for c in text
            if unicodedata.category(c) != "Mn"
        )
        text = text.replace(":", "").replace(",", "")

        return (
            text
            .replace(" ", "_")
            .replace("/", "_")
            .replace("(", "")
            .replace(")", "")
        )

  
    def build_chunk(self, family, culture, section):

        text = self.build_text(
            family,
            culture,
            section
        )

        chunk_id = (
            f"{self.normalize(family.nom)}_"
            f"{self.normalize(culture.nom)}_"
            f"{self.normalize(section.nom)}_"
            f"p{section.page}"
        )

        return Chunk(
            id=chunk_id,
            culture=culture.nom,
            text=text,
            metadata={
                "family": family.nom,
                "culture": culture.nom,
                "section": section.nom,
                "page": section.page,
            }
        )


    def format_entry(self, entry):

        parts = [p.strip() for p in entry.text.split("|")]

        if len(parts) >= 3:
            return (
                f"• Usage : {parts[1]}\n"
                f"  Cible : {parts[2]}"
            )

        return entry.text


    def build_text(self, family, culture, section):
        """
        Reconstruit le texte envoyé au modèle d'embedding.
        Un chunk = une seule section.
        """

        lines = [
            f"FAMILLE : {family.nom}",
            f"CULTURE : {culture.nom}",
            f"SECTION : {section.nom}",
            ""
        ]

        for entry in section.entries:
            lines.append(self.format_entry(entry))
            lines.append("")

        return "\n".join(lines)