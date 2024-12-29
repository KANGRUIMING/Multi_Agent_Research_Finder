# webapp.py

from flask import Flask, render_template, request
from latest_ai_development.crew import LatestAiDevelopment
from pydantic import ValidationError

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route:
      1) Collects user inputs (topic, university, resume).
      2) Calls the AI (Crew).
      3) Extracts 'professors' and 'labs' with try/except to avoid KeyError.
    """
    parsed_data = None
    raw_result = None

    if request.method == "POST":
        topic = request.form.get("topic", "")
        university = request.form.get("university", "")
        resume = request.form.get("resume", "")

        inputs = {
            "topic": topic,
            "university": university,
            "resume": resume,
        }

        crew_instance = LatestAiDevelopment().crew()
        try:
            # 'result' is a CrewOutput object
            result = crew_instance.kickoff(inputs=inputs)

            # Convert the entire result to string for fallback display
            raw_result = str(result)

            # Attempt to retrieve 'professors' and 'labs' keys
            try:
                professors = result["professors"]
            except KeyError:
                professors = []

            try:
                labs = result["labs"]
            except KeyError:
                labs = []

            # If either has data, we store them in parsed_data
            if professors or labs:
                parsed_data = {
                    "professors": professors,
                    "labs": labs
                }

        except ValidationError as e:
            raw_result = f"Error validating AI output: {str(e)}"
        # You could catch other exceptions if needed

    return render_template("index.html", data=parsed_data) # , result=raw_result


@app.route("/select", methods=["POST"])
def select():
    """
    Captures 'Select' button presses (professors or labs).
    """
    prof_name = request.form.get("name")
    prof_email = request.form.get("contact_email")
    lab_name = request.form.get("name_lab")
    lab_url = request.form.get("url_lab")

    if prof_name and prof_email:
        selection_message = f"You selected professor: {prof_name}, email: {prof_email}"
    elif lab_name and lab_url:
        selection_message = f"You selected lab: {lab_name}, URL: {lab_url}"
    else:
        selection_message = "Nothing selected or missing data."

    return f"<h2>{selection_message}</h2><p><a href='/'>Back to Home</a></p>"


if __name__ == "__main__":
    app.run(debug=True)
