# webapp.py

from flask import Flask, render_template, request
from latest_ai_development.crew import LatestAiDevelopment

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        # Get data from the form fields
        topic = request.form.get("topic", "")
        university = request.form.get("university", "")
        resume = request.form.get("resume", "")

        # Prepare inputs dictionary
        inputs = {
            'topic': topic,
            'university': university,
            'resume': resume,
        }

        # Kick off the AI dev crew
        # If your tasks/agents return an output, you might store it in `result`
        crew_instance = LatestAiDevelopment().crew()
        result = crew_instance.kickoff(inputs=inputs)

        # `result` could be None or some data structure, depending on how your tasks are configured.
        # If tasks produce textual output, store it here so you can display it.

    return render_template("index.html", result=result)

if __name__ == "__main__":
    # Set debug=True only during development
    app.run(debug=True)
