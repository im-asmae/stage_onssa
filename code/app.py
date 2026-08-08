from flask import Flask, render_template, request

from rag.pipeline import RAGPipeline


pipeline = RAGPipeline()
app = Flask(__name__)

question = ""
@app.route("/", methods=["GET", "POST"])
def home():

    answer = None
    results = None
    question = ""

    if request.method == "POST":

        question = request.form["question"]

        answer, results = pipeline.ask(question)

    if answer :
        answer=answer.replace("\n", "<br>")
    return render_template(
        "index.html",
        question=question,
        answer=answer,
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)