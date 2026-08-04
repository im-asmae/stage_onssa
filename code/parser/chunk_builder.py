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

                chunk = self.build_chunk(
                    family,
                    culture
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

        return (
            text
            .replace(" ", "_")
            .replace("/", "_")
            .replace("(", "")
            .replace(")", "")
        )

  
    def build_chunk(self, family, culture):
        """
        Construit un chunk correspondant à une culture.
        """

        text = self.build_text(
            family,
            culture
        )

        chunk_id = f"{self.normalize(family.nom)}_{self.normalize(culture.nom)}"

        return Chunk(
            id = chunk_id,
            culture=culture.nom,
            text=text,
            metadata={
                "family" : family.nom,
                "page" : culture.page,
            }
        )


    def build_text(self, family, culture):
        """
        Reconstruit le texte qui sera envoyé au modèle d'embedding.
        """

        lines = [
            f"Famille : {family.nom}",
            f"Culture : {culture.nom}",
            ""
        ]

        for section in culture.sections:

            lines.append(section.nom)

            for entry in section.entries:
                lines.append(f"- {entry.text}")

            lines.append("")

        return "\n".join(lines)