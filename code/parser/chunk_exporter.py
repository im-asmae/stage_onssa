import json


class ChunkExporter:

    def export(self, chunks, output_path):

        data = []

        for chunk in chunks:

            data.append(
                {
                    "id": chunk.id,
                    "culture": chunk.culture,
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                }
            )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)