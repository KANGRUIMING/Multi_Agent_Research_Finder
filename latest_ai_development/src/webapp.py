import uuid
from flask import Flask, render_template, request, session
from pydantic import ValidationError
from latest_ai_development.crew import LatestAiDevelopment

app = Flask(__name__)
app.secret_key = "REPLACE_WITH_A_STRONG_SECRET_KEY"

# In-memory store: { user_id: {...} }
app_data_store = {}

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route:
      - GET: Renders the form for 'topic', 'university', 'resume'.
      - POST: Calls .kickoff() to run the Crew AI pipeline, then extracts professors/labs from final output.
    """
    user_id = session.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id

    if user_id not in app_data_store:
        app_data_store[user_id] = {
            "professors": [],
            "labs": [],
            "raw_result": None
        }

    user_data = app_data_store[user_id]

    if request.method == "POST":
        topic = request.form.get("topic", "")
        university = request.form.get("university", "")
        resume = request.form.get("resume", "")

        inputs = {
            "topic": topic,
            "university": university,
            "resume": resume,
        }

        # Kick off the entire AI crew
        crew_instance = LatestAiDevelopment().crew()
        try:
            result = crew_instance.kickoff(inputs=inputs)
            # Convert the entire final output to a string for fallback display
            user_data["raw_result"] = str(result)

            # Safely extract 'professors' and 'labs' 
            try:
                professors = result["professors"]  # might raise KeyError
            except KeyError:
                professors = []
            try:
                labs = result["labs"]  # might raise KeyError
            except KeyError:
                labs = []

            # Store them in memory
            user_data["professors"] = professors
            user_data["labs"] = labs

        except ValidationError as e:
            user_data["raw_result"] = f"Error validating AI output: {str(e)}"
        # You can catch other exceptions if needed

    # Render the page with stored data
    return render_template(
        "index.html",
        data={
            "professors": user_data["professors"],
            "labs": user_data["labs"]
        },
        result=user_data["raw_result"]
    )

@app.route("/select", methods=["POST"])
def select():
    """
    When the user selects a professor or lab from the list,
    we read the hidden fields and display a simple confirmation.
    (Optional) you can integrate deeper research tasks here.
    """
    user_id = session.get("user_id")
    if not user_id or user_id not in app_data_store:
        return "Session not found, please go back to home."

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
