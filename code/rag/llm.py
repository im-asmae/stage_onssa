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


    def generate(self, question, context):
        """
        Génère une réponse à partir du contexte fourni par le Retriever.
        """

        prompt = self.build_prompt(
            question=question,
            context=context
        )


        response = self.client.chat(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": """
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
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            options={
                "temperature": self.temperature
            }
        )


        return response["message"]["content"].strip()



    def build_prompt(
        self,
        question,
        context
    ):
        """
        Construction du prompt utilisateur.
        """

        return f"""
            Tu es un assistant spécialisé dans le Référentiel des usages agricoles de l'ONSSA.
            Le contexte qui te sera fourni provient du Retriever du système RAG.

            Considère que ce contexte est le plus pertinent disponible.

            N'utilise jamais de connaissances externes et n'invente aucune information.

            ==============================
            CONTEXTE
            ==============================

            {context}

            ==============================
            QUESTION
            ==============================

            {question}

        ==============================
        INSTRUCTIONS
        ==============================

        Réponds à la question en utilisant UNIQUEMENT le CONTEXTE.

        RÈGLE PRINCIPALE :
        Lorsque la question demande les éléments d'une SECTION pour une CULTURE,
        retourne TOUTES les valeurs du champ « Cible » présentes dans cette section
        pour cette culture.

        Pour la question :
        « Quels sont les ravageurs du rosier ? »

        il faut donc retourner toutes les cibles présentes dans :
        [Cultures ornementales > Rosier > Ravageurs]

        Dans cette section, les cibles sont :
        - Nématodes
        - Acariens
        - Mouches blanches
        - Noctuelles défoliatrices
        - Cochenilles
        - Pucerons
        - Insectes

        IMPORTANT :
        - Ne supprime aucune cible.
        - Ne filtre jamais les cibles selon leur « Usage ».
        - « traitement du sol », « Parties aériennes » et « Trt post-récolte »
          sont tous des usages valides.
        - Une cible reste valide même si son usage est différent des autres.
        - Ne remplace pas une cible par une autre.
        - Ne sélectionne pas uniquement les cibles qui te semblent être des
          ravageurs classiques.
        - Le référentiel fait foi : restitue exactement les valeurs présentes
          dans le champ « Cible ».
        - Si 7 cibles sont présentes dans la section correspondante,
          la réponse doit contenir les 7 cibles.
        - N'utilise aucune connaissance externe pour décider si une cible
          est ou n'est pas un ravageur.
        - Ne déduis rien à partir de tes connaissances générales.

        Pour chaque cible, conserve son nom tel qu'il apparaît dans le contexte.

        Si plusieurs cultures apparaissent dans le contexte, utilise uniquement
        la culture demandée dans la question.

        Si la section demandée est présente, utilise uniquement cette section.

        Si aucune information correspondant à la culture et à la section
        demandées n'est présente dans le contexte, réponds exactement :

        Cette information n'est pas présente dans le référentiel ONSSA fourni.

        Réponds en français de manière claire et concise.
        """