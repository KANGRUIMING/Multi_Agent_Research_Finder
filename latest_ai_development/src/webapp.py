import json
from flask import Flask, render_template, request
from latest_ai_development.crew import LatestAiDevelopment
from pydantic import ValidationError

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route:
      - On POST, calls your Crew AI with user inputs (topic, university, resume).
      - Attempts to parse out 'professors' and 'labs' from the AI result,
        then writes them to 'outputs/research_info.json'.
      - After that (or on GET), loads 'outputs/research_info.json' to display
        any saved professors/labs in the template.
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
            # Call your Crew AI
            result = crew_instance.kickoff(inputs=inputs)
            raw_result = str(result)  # For fallback display

            # Attempt to extract 'professors' and 'labs' from the CrewOutput
            try:
                professors = result["professors"]
            except KeyError:
                professors = []

            try:
                labs = result["labs"]
            except KeyError:
                labs = []

            # If we got any professors or labs, save them to the JSON file
            if professors or labs:
                data_to_write = {
                    "professors": professors,
                    "labs": labs
                }
                with open("outputs/research_info.json", "w", encoding="utf-8") as f:
                    json.dump(data_to_write, f, indent=4)

        except ValidationError as e:
            raw_result = f"Error validating AI output: {str(e)}"
        # You can add more exception handling if needed.

    # Now, whether GET or POST, read from 'outputs/research_info.json'
    try:
        with open("outputs/research_info.json", "r", encoding="utf-8") as f:
            file_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or has invalid JSON, we default to an empty dict
        file_data = {}

    # Safely extract professors/labs from the file
    professors = file_data.get("professors", [])
    labs = file_data.get("labs", [])

    # If we have any data, store it for the template
    if professors or labs:
        parsed_data = {
            "professors": professors,
            "labs": labs
        }

    # Render the template with either parsed_data or raw_result fallback
    return render_template("index.html", data=parsed_data, result=raw_result)


@app.route("/select", methods=["POST"])
def select():
    """
    Captures 'Select' button presses (professors or labs).
    Reads the hidden fields from the form and displays a simple message.
    """
    prof_name = request.form.get("prof_name")
    prof_email = request.form.get("prof_email")
    lab_name = request.form.get("lab_name")
    lab_url = request.form.get("lab_url")

    if prof_name and prof_email:
        selection_message = f"You selected professor: {prof_name}, email: {prof_email}"
    elif lab_name and lab_url:
        selection_message = f"You selected lab: {lab_name}, URL: {lab_url}"
    else:
        selection_message = "Nothing selected or missing data."

    return f"<h2>{selection_message}</h2><p><a href='/'>Back to Home</a></p>"


if __name__ == "__main__":
    app.run(debug=True)
