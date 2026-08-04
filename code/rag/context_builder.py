class ContextBuilder:
    """
    Transforme les résultats du Retriever
    en un contexte qui sera envoyé au LLM.
    """

    def build(self, results):

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        ids = results["ids"][0]

        lines = []

        lines.append(
            "Le contexte suivant est extrait du référentiel officiel de l'ONSSA."
        )
        lines.append(
            "Réponds uniquement à partir de ces informations."
        )
        lines.append("")

        for i, (doc, meta, chunk_id) in enumerate(
            zip(documents, metadatas, ids),
            start=1
        ):

            lines.append("=" * 60)
            lines.append(f"DOCUMENT {i}")
            lines.append("=" * 60)

            lines.append(f"ID : {chunk_id}")
            lines.append(f"Famille : {meta['family']}")
            lines.append(f"Culture : {meta['culture']}")
            lines.append(f"Page : {meta['page']}")
            lines.append("")

            lines.append(doc)
            lines.append("")

        return "\n".join(lines)