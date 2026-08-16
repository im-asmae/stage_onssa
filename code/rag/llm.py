# from ollama import Client


# class LLM:
#     """
#     Interface avec un modèle Ollama local.
#     """

#     def __init__(
#         self,
#         model="qwen2.5:7b",
#         temperature=0.1
#     ):

#         self.model = model
#         self.temperature = temperature

#         # Connexion explicite au serveur Ollama
#         self.client = Client(
#             host="http://127.0.0.1:11434"
#         )


#     def generate(self, question, context):
#         """
#         Génère une réponse à partir du contexte fourni par le Retriever.
#         """

#         prompt = self.build_prompt(
#             question=question,
#             context=context
#         )


#         response = self.client.chat(

#             model=self.model,

#             messages=[
#                 {
#                     "role": "system",
#                     "content": """
# Tu es un assistant spécialisé dans le Référentiel des usages agricoles de l'ONSSA.

# Règles obligatoires :

# 1. Réponds uniquement à partir du contexte fourni.
# 2. N'utilise aucune connaissance externe.
# 3. N'invente jamais une information.
# 4. Si plusieurs cultures apparaissent, utilise uniquement celle demandée.
# 5. Si l'information est absente, réponds :

# "Cette information n'est pas présente dans le référentiel ONSSA fourni."

# 6. Ne propose aucun traitement, pesticide ou matière active absent du contexte.
# 7. Réponds en français avec un style professionnel.
# """
#                 },

#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ],

#             options={
#                 "temperature": self.temperature
#             }
#         )


#         return response["message"]["content"].strip()



#     def build_prompt(
#         self,
#         question,
#         context
#     ):
#         """
#         Construction du prompt utilisateur.
#         """

#         return f"""
#             Tu es un assistant spécialisé dans le Référentiel des usages agricoles de l'ONSSA.
#             Le contexte qui te sera fourni provient du Retriever du système RAG.

#             Considère que ce contexte est le plus pertinent disponible.

#             N'utilise jamais de connaissances externes et n'invente aucune information.

#             ==============================
#             CONTEXTE
#             ==============================

#             {context}

#             ==============================
#             QUESTION
#             ==============================

#             {question}

#         ==============================
#         INSTRUCTIONS
#         ==============================

#         Réponds à la question en utilisant UNIQUEMENT le CONTEXTE.

#         RÈGLE D'EXTRACTION :

#         Pour une question de la forme :

#         « Quels sont les [éléments] de [culture] ? »

#         tu dois effectuer une extraction directe depuis le CONTEXTE.

#         ÉTAPES OBLIGATOIRES :

#         1. Identifie dans le contexte la CULTURE demandée.
#         2. Identifie dans le contexte la SECTION demandée.
#         3. Sélectionne uniquement le bloc correspondant à cette CULTURE et cette SECTION.
#         4. Dans ce bloc, lis CHAQUE ligne commençant par :
#         « Cible : »
#         5. Retourne TOUTES les valeurs trouvées après « Cible : ».
#         6. Ne supprime aucune valeur.
#         7. Ne sélectionne pas les cibles selon leur Usage.
#         8. Ne juge pas si une cible est réellement un ravageur selon tes connaissances.
#         9. Le référentiel ONSSA est la seule source de vérité.

#         EXEMPLE EXACT :

#         CONTEXTE :

#         [Cultures tropicales > Bananier > Ravageurs]

#         • Usage : traitement du sol
#         Cible : Nématodes

#         • Usage : Parties aériennes
#         Cible : Acariens

#         • Usage : Parties aériennes
#         Cible : Mouches blanches

#         • Usage : Parties aériennes
#         Cible : Noctuelles défoliatrices

#         QUESTION :

#         Quels sont les ravageurs du bananier ?

#         EXTRACTION DES CIBLES :

#         Cible : Nématodes
#         Cible : Acariens
#         Cible : Mouches blanches
#         Cible : Noctuelles défoliatrices

#         RÉPONSE OBLIGATOIRE :

#         - Nématodes
#         - Acariens
#         - Mouches blanches
#         - Noctuelles défoliatrices

#         IMPORTANT :
#         Le nombre de cibles dans la réponse doit être exactement égal au nombre
#         de lignes « Cible : » présentes dans le bloc correspondant.

#         Dans l'exemple ci-dessus, il y a 4 lignes « Cible : ».
#         La réponse doit donc contenir exactement 4 cibles.

#         Une cible ne peut être ignorée sous aucun prétexte si elle apparaît dans
#         le bloc correspondant.


#         Si plusieurs cultures apparaissent dans le contexte, utilise uniquement
#         la culture demandée dans la question.

#         Si la section demandée est présente, utilise uniquement cette section.

#         Si aucune information correspondant à la culture et à la section demandées n'est présente dans le contexte, réponds exactement : Cette information n'est pas présente dans le référentiel ONSSA fourni.

#         Réponds en français de manière claire et concise.
#         """

import re

from ollama import Client


class LLM:
    """
    Interface avec un modèle Ollama local.
    """

    def __init__(
        self,
        model="qwen2.5:7b",
        temperature=0.1
    ):

        self.model = model
        self.temperature = temperature

        # Connexion explicite au serveur Ollama
        self.client = Client(
            host="http://127.0.0.1:11434"
        )

    # ------------------------------------------------------------------
    # Détection du type de question
    # ------------------------------------------------------------------

    def is_extraction_question(self, question: str) -> bool:
        """
        Détecte si la question correspond au pattern
        « Quels sont les [éléments] de [culture] ? »

        Ce type de question a une réponse déterministe : la liste
        complète des lignes "Cible :" du bloc contexte correspondant.
        On ne veut PAS laisser le LLM décider quoi inclure ou exclure.
        """

        pattern = r"quels?\s+sont\s+les\s+.+\s+(du|de|des|de la|de l')\s+.+"
        return re.search(pattern, question.strip(), flags=re.IGNORECASE) is not None

    # ------------------------------------------------------------------
    # Extraction déterministe des cibles depuis le contexte
    # ------------------------------------------------------------------

    def extract_cibles(self, context: str) -> list[str]:
        """
        Extrait de façon 100% fiable toutes les valeurs qui suivent
        "Cible :" dans le contexte fourni par le Retriever.

        Aucun LLM impliqué ici : c'est du simple parsing texte, donc
        aucun biais de "connaissance générale" ne peut faire disparaître
        une cible (ex: les nématodes systématiquement exclus).
        """

        cibles = re.findall(r"Cible\s*:\s*(.+)", context)

        # Nettoyage (espaces, retours à la ligne parasites) + dédoublonnage
        # en conservant l'ordre d'apparition
        seen = set()
        result = []
        for c in cibles:
            c_clean = c.strip()
            if c_clean and c_clean not in seen:
                seen.add(c_clean)
                result.append(c_clean)

        return result

    # ------------------------------------------------------------------
    # Génération
    # ------------------------------------------------------------------

    def generate(self, question, context):
        """
        Génère une réponse à partir du contexte fourni par le Retriever.

        Deux modes :
        - Mode extraction : question du type "Quels sont les X de Y ?"
          -> extraction déterministe des cibles (regex), puis le LLM
             ne sert qu'à formuler la réponse, sans pouvoir en retirer.
        - Mode général : toute autre question -> prompt RAG classique.
        """

        if self.is_extraction_question(question):
            return self._generate_extraction(question, context)

        return self._generate_general(question, context)

    def _call_llm(self, system_content, user_content):
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
            options={
                "temperature": self.temperature
            }
        )
        return response["message"]["content"].strip()

    # ------------------------------------------------------------------
    # Mode extraction (déterministe + mise en forme LLM)
    # ------------------------------------------------------------------

    def _generate_extraction(self, question, context):

        cibles = self.extract_cibles(context)

        if not cibles:
            return "Cette information n'est pas présente dans le référentiel ONSSA fourni."

        system_content = """
Tu es un assistant spécialisé dans le Référentiel des usages agricoles de l'ONSSA.
Tu ne fais que reformuler une liste déjà validée. Tu n'as pas le droit de la modifier.
"""

        liste_formattee = "\n".join(f"- {c}" for c in cibles)

        user_content = f"""
QUESTION :
{question}

LISTE EXACTE ET COMPLÈTE (déjà extraite et validée, ne pas modifier) :
{liste_formattee}

INSTRUCTIONS :
- Réponds à la question en présentant CETTE LISTE sous forme de liste à puces.
- N'ajoute, ne supprime, ne fusionne, ne reformule AUCUN élément de la liste.
- N'ajoute aucun commentaire, aucune explication, aucune connaissance externe.
- Le nombre d'éléments dans ta réponse doit être exactement {len(cibles)}.
- Réponds en français.
"""

        answer = self._call_llm(system_content, user_content)

        # Filet de sécurité : si le LLM a quand même perdu des éléments
        # (rare une fois qu'il n'a plus qu'à recopier), on retombe sur
        # la liste déterministe brute.
        missing = [c for c in cibles if c.lower() not in answer.lower()]
        if missing:
            return liste_formattee

        return answer

    # ------------------------------------------------------------------
    # Mode général (questions non listables : explications, comparaisons...)
    # ------------------------------------------------------------------

    def _generate_general(self, question, context):

        system_content = """
Tu es un assistant spécialisé dans le Référentiel des usages agricoles de l'ONSSA.

Règles obligatoires :

1. Réponds uniquement à partir du contexte fourni.
2. N'utilise aucune connaissance externe.
3. N'invente jamais une information.
4. Si plusieurs cultures apparaissent, utilise uniquement celle demandée.
5. Si l'information est absente, réponds :

"Cette information n'est pas présente dans le référentiel ONSSA fourni."

6. Ne propose aucun traitement, pesticide ou matière active absent du contexte.
7. Réponds en français avec un style professionnel.
"""

        user_content = self.build_prompt(question=question, context=context)

        return self._call_llm(system_content, user_content)

    def build_prompt(
        self,
        question,
        context
    ):
        """
        Construction du prompt utilisateur pour les questions générales
        (non listables). Pour les questions d'extraction, voir
        _generate_extraction qui n'utilise pas cette méthode.
        """

        return f"""
CONTEXTE
========
{context}

QUESTION
========
{question}

INSTRUCTIONS
============
Réponds à la question en utilisant UNIQUEMENT le CONTEXTE.
N'utilise jamais de connaissances externes et n'invente aucune information.
Si l'information demandée n'est pas présente dans le CONTEXTE, réponds exactement :
"Cette information n'est pas présente dans le référentiel ONSSA fourni."
Réponds en français de manière claire et concise.
"""