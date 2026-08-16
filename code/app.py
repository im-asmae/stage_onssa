from flask import Flask, render_template, request
from rag.pipeline import RAGPipeline


app = Flask(__name__)
pipeline = RAGPipeline()


@app.route("/", methods=["GET", "POST"])
def home():

    answer = None
    results = []
    question = ""

    if request.method == "POST":

        question = request.form.get("question", "").strip()

        if question:
            answer, results = pipeline.ask(question)

    return render_template(
        "index.html",
        question=question,
        answer=answer,
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)