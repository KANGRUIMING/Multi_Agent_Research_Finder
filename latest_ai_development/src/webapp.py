import uuid
from flask import Flask, render_template, request, session
from latest_ai_development.crew import LatestAiDevelopment
from pydantic import ValidationError

app = Flask(__name__)

# Required for using session
app.secret_key = "REPLACE_WITH_A_STRONG_SECRET_KEY"

# In-memory store: { user_id: {"professors": [...], "labs": [...], "raw_result": "..."}}
app_data_store = {}

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route:
      1) If a user_id is not in the session, create one.
      2) Ensure there's an entry in app_data_store for this user.
      3) On POST, call the Crew AI and store the result in memory for this user.
      4) Pass the user's data to the template for display.
    """
    # 1) Identify the user via session
    user_id = session.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())  # Generate a unique ID
        session["user_id"] = user_id

    # 2) Ensure an entry exists in app_data_store for this user
    if user_id not in app_data_store:
        app_data_store[user_id] = {
            "professors": [],
            "labs": [],
            "raw_result": None
        }

    user_data = app_data_store[user_id]

    # 3) If POST, call the Crew AI with the user’s inputs
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
            result = crew_instance.kickoff(inputs=inputs)
            # Store the entire raw output for fallback display
            user_data["raw_result"] = str(result)

            # Attempt to extract 'professors' & 'labs' from the CrewOutput
            try:
                professors = result["professors"]
            except KeyError:
                professors = []

            try:
                labs = result["labs"]
            except KeyError:
                labs = []

            # Update the user's in-memory data
            user_data["professors"] = professors
            user_data["labs"] = labs

        except ValidationError as e:
            user_data["raw_result"] = f"Error validating AI output: {str(e)}"
        # Additional exception handling can be done here

    # 4) Pass the user's data to the template
    return render_template(
        "index.html",
        data={
            "professors": user_data["professors"],
            "labs": user_data["labs"],
        },
        result=user_data["raw_result"]
    )

@app.route("/select", methods=["POST"])
def select():
    """
    Captures 'Select' button presses (professors or labs).
    Reads the hidden fields posted from the form and displays a confirmation.
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