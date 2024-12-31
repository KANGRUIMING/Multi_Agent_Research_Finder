# webapp.py

import uuid
import json
from flask import Flask, render_template, request, session, jsonify
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
            "raw_result": None,
            "resume": "",
        }

    user_data = app_data_store[user_id]

    if request.method == "POST":
        topic = request.form.get("topic", "")
        university = request.form.get("university", "")
        resume = request.form.get("resume", "")

        # Store the resume for potential use later (e.g. cover letter)
        user_data["resume"] = resume

        inputs = {
            "topic": topic,
            "university": university,
            "resume": resume,
        }

        # Kick off the entire AI crew (unchanged)
        crew_instance = LatestAiDevelopment().crew()
        try:
            result = crew_instance.kickoff(inputs=inputs)
            user_data["raw_result"] = str(result)

            try:
                professors = result["professors"]
            except KeyError:
                professors = []
            try:
                labs = result["labs"]
            except KeyError:
                labs = []

            user_data["professors"] = professors
            user_data["labs"] = labs

        except ValidationError as e:
            user_data["raw_result"] = f"Error validating AI output: {str(e)}"

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

########################################
# Route that only runs the 'researcher' agent
# Does NOT invoke deeper_researcher or cover_letter_agent
########################################
@app.route("/researcher_phase", methods=["GET", "POST"])
def researcher_phase():
    """
    - GET: Renders a form for topic/university/resume
    - POST: Runs only the 'researcher' agent (not the entire crew).
      Expects JSON with 'professors' and 'labs' in the output.
    - Renders index.html to display the returned data so the user can select.
    """
    user_id = session.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id

    # Create user data in the in-memory store if missing
    if user_id not in app_data_store:
        app_data_store[user_id] = {
            "professors": [],
            "labs": [],
            "raw_result": None,
            "resume": "",
        }

    user_data = app_data_store[user_id]

    if request.method == "POST":
        topic = request.form.get("topic", "")
        university = request.form.get("university", "")
        resume = request.form.get("resume", "")

        user_data["resume"] = resume  # store resume for later

        # We'll pass these as JSON to the researcher agent
        user_input = json.dumps({
            "topic": topic,
            "university": university,
            "resume": resume
        })

        # 1) Only get the 'researcher' agent
        researcher_agent = LatestAiDevelopment().researcher()

        # 2) Call agent.run(...)
        raw_result = researcher_agent.run(user_input)

        # 3) Attempt to parse JSON for { "professors": [...], "labs": [...] }
        try:
            parsed_json = json.loads(raw_result)
        except json.JSONDecodeError:
            # If not valid JSON, just store the raw result
            parsed_json = {}

        professors = parsed_json.get("professors", [])
        labs = parsed_json.get("labs", [])

        # 4) Store in memory
        user_data["professors"] = professors
        user_data["labs"] = labs
        user_data["raw_result"] = raw_result

    # Render same template to display the data
    return render_template(
        "index.html",
        data={
            "professors": user_data["professors"],
            "labs": user_data["labs"]
        },
        result=user_data["raw_result"]
    )


########################################
# 1) Route to run the deeper_researcher agent
########################################
@app.route("/run_deeper_research", methods=["POST"])
def run_deeper_research():
    """
    Trigger the deeper_researcher agent for additional info on a selected professor (or lab).
    """
    user_id = session.get("user_id")
    if not user_id or user_id not in app_data_store:
        return "Session not found, please go back to home."

    user_data = app_data_store[user_id]

    prof_name = request.form.get("prof_name", "")
    prof_url = request.form.get("prof_url", "")

    # Prepare input JSON for deeper researcher
    deeper_input = json.dumps({
        "prof_name": prof_name,
        "prof_url": prof_url,
    })

    deeper_agent = LatestAiDevelopment().deeper_researcher()
    raw_result = deeper_agent.run(deeper_input)

    # The deeper_researcher is supposed to return JSON matching SpecificProfessorInfo:
    # {
    #    "publications": [...],
    #    "projects": [...],
    #    "courses": [...]
    # }
    try:
        parsed_json = json.loads(raw_result)
    except json.JSONDecodeError:
        parsed_json = {}

    # Optionally, store deeper info in user_data if you want to display it
    user_data["raw_result"] = raw_result
    user_data["publications"] = parsed_json.get("publications", [])
    user_data["projects"] = parsed_json.get("projects", [])
    user_data["courses"] = parsed_json.get("courses", [])

    # Rerender index.html (or a new template) to show deeper info
    return render_template(
        "index.html",
        data={
            "professors": user_data["professors"],
            "labs": user_data["labs"]
            # If you want to display deeper info, you'd pass it here or create a new template
        },
        result=user_data["raw_result"]
    )


########################################
# 2) Route to run the cover_letter_agent
########################################
@app.route("/run_cover_letter", methods=["POST"])
def run_cover_letter():
    """
    Trigger the cover_letter_agent for a selected professor (or lab),
    using the user's stored resume to generate a cover letter.
    """
    user_id = session.get("user_id")
    if not user_id or user_id not in app_data_store:
        return "Session not found, please go back to home."

    user_data = app_data_store[user_id]

    prof_name = request.form.get("prof_name", "")
    prof_url = request.form.get("prof_url", "")
    resume = user_data.get("resume", "")

    # Prepare JSON for cover letter agent
    cover_input = json.dumps({
        "prof_name": prof_name,
        "prof_url": prof_url,
        "resume": resume
    })

    cover_agent = LatestAiDevelopment().cover_letter_agent()
    raw_result = cover_agent.run(cover_input)

    # The cover_letter_agent should return JSON matching CoverLetterOutput:
    # {
    #    "email_subject": "...",
    #    "email_body": "...",
    #    "cover_letter": "..."
    # }
    try:
        parsed_json = json.loads(raw_result)
    except json.JSONDecodeError:
        parsed_json = {}

    user_data["raw_result"] = raw_result
    user_data["email_subject"] = parsed_json.get("email_subject", "")
    user_data["email_body"]    = parsed_json.get("email_body", "")
    user_data["cover_letter"]  = parsed_json.get("cover_letter", "")

    # You can create a new template to display the subject/body/cover_letter,
    # or just reuse index.html for demonstration:
    return render_template(
        "index.html",
        data={
            "professors": user_data["professors"],
            "labs": user_data["labs"]
        },
        result=user_data["raw_result"]
    )


# Main entry point
if __name__ == "__main__":
    app.run(debug=True)
