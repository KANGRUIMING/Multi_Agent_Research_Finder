import uuid
from flask import Flask, render_template, request, session
from pydantic import ValidationError

# --- Renamed classes/crews ---
# Adjust these import statements to match your actual file/module paths
from latest_ai_development.crew import Crew1
from latest_ai_development_copy.crew import Crew2
from latest_ai_development_copy_copy.crew import Crew3

app = Flask(__name__)

# Required for using session
app.secret_key = "REPLACE_WITH_A_STRONG_SECRET_KEY"

# In-memory store: { user_id: {"professors": [...], "labs": [...], "raw_result": "...", "crew1_output": {...}, "crew2_output": {...}} }
app_data_store = {}


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route:
      1) If a user_id is not in the session, create one.
      2) Ensure there's an entry in app_data_store for this user.
      3) On POST, call Crew1 and store the result in memory for this user.
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
            "raw_result": None,
            "university": None,
            "resume": None,
            "crew1_output": None,  # Will store memory from Crew1
            "crew2_output": None,  # Will store memory from Crew2
        }

    user_data = app_data_store[user_id]

    # 3) If POST, call Crew1 with the user’s inputs
    if request.method == "POST":
        topic = request.form.get("topic", "")
        university = request.form.get("university", "")
        resume = request.form.get("resume", "")

        user_data["university"] = university
        user_data["resume"] = resume

        inputs = {
            "topic": topic,
            "university": university,
            "resume": resume,
        }

        # Instantiate Crew1
        crew_instance = Crew1().crew()
        try:
            result = crew_instance.kickoff(inputs=inputs)
            # Store the entire raw output for fallback display
            user_data["raw_result"] = str(result)
            # Keep Crew1's output in memory for subsequent usage
            user_data["crew1_output"] = result

            # Attempt to extract 'professors' & 'labs' from the Crew1 output
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
    Also demonstrates how Crew2 and Crew3 can use Crew1's memory.
    """
    user_id = session.get("user_id")
    user_data = app_data_store.get(user_id, {})

    university = user_data.get("university", "")
    resume = user_data.get("resume", "")

    prof_name = request.form.get("prof_name")
    prof_email = request.form.get("prof_email")
    lab_name = request.form.get("lab_name")
    lab_url = request.form.get("lab_url")

    selection_message = ""
    raw_result = ""
    letter_result = ""

    # If the user selects a professor
    if prof_name and prof_email:
        selection_message = f"You selected professor: {prof_name}, email: {prof_email}"

        # Retrieve Crew1 memory
        crew1_memory = user_data.get("crew1_output", {})

        # --------------------------------------------------
        # Call Crew2 with both user input and Crew1 memory
        # --------------------------------------------------
        inputs_crew2 = {
            "prof_name": prof_name,
            "prof_email": prof_email,
            "university": university,
            "lab_name": lab_name,
            "previous_crew_output": crew1_memory
        }
        crew2_instance = Crew2().crew()
        try:
            result_crew2 = crew2_instance.kickoff(inputs=inputs_crew2)
            raw_result = str(result_crew2)

            # Store Crew2's memory if you want to use it later
            user_data["crew2_output"] = result_crew2
        except ValidationError as e:
            raw_result = f"Error validating AI output: {str(e)}"

        # --------------------------------------------------
        # Call Crew3 (optionally including Crew2 output)
        # --------------------------------------------------
        # Suppose Crew3 needs the resume and any data from Crew2
        letterinputs_crew3 = {
            "resume": resume,
            "prof_name": prof_name,
            "crew2_data": user_data.get("crew2_output", {})
        }
        crew3_instance = Crew3().crew()
        try:
            result_crew3 = crew3_instance.kickoff(inputs=letterinputs_crew3)
            letter_result = str(result_crew3)
        except ValidationError as e:
            letter_result = f"Error validating AI output: {str(e)}"

    # If the user selects a lab
    elif lab_name and lab_url:
        selection_message = f"You selected lab: {lab_name}, URL: {lab_url}"

        # Retrieve Crew1 memory
        crew1_memory = user_data.get("crew1_output", {})

        # --------------------------------------------------
        # Call Crew2 with lab info + Crew1 memory
        # --------------------------------------------------
        inputs_crew2 = {
            "lab_name": lab_name,
            "lab_url": lab_url,
            "university": university,
            "previous_crew_output": crew1_memory
        }
        crew2_instance = Crew2().crew()
        try:
            result_crew2 = crew2_instance.kickoff(inputs=inputs_crew2)
            raw_result = str(result_crew2)
        except ValidationError as e:
            raw_result = f"Error validating AI output: {str(e)}"

        # For labs, we might skip Crew3 or handle similarly
        # letter_result left blank, or do something else
        letter_result = ""

    else:
        selection_message = "Nothing selected or missing data."

    return f"""
        <h2>Selection Message:</h2>
        <p>{selection_message}</p>
        <h2>Raw Result (Crew2):</h2>
        <pre>{raw_result}</pre>
        <h2>Letter Result (Crew3):</h2>
        <pre>{letter_result}</pre>
        <p><a href="/">Back to Home</a></p>
    """


if __name__ == "__main__":
    app.run(debug=True)
