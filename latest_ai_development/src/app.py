# app.py

import json
from flask import Flask, render_template, request

app = Flask(__name__)

# This is your JSON (hardcoded here as a string for demonstration).
json_data = """
{
    "professors": [
        {
            "name": "Ben Abbatematteo",
            "research_interests": "AI, Machine Learning",
            "contact_email": "ben.abbat@utexas.edu",
            "url": "https://www.cs.utexas.edu/people/ben-abbatamatteo"
        },
        {
            "name": "Joydeep Biswas",
            "research_interests": "AI, Robotics",
            "contact_email": "joydeep@utexas.edu",
            "url": "https://www.cs.utexas.edu/people/joydeep-biswas"
        },
        {
            "name": "William Bulko",
            "research_interests": "AI, Computer Vision",
            "contact_email": "wb@utexas.edu",
            "url": "https://www.cs.utexas.edu/people/william-bulko"
        },
        {
            "name": "Rohan Chandra",
            "research_interests": "AI, Algorithm Development",
            "contact_email": "rohan@utexas.edu",
            "url": "https://www.cs.utexas.edu/people/rohan-chandra"
        },
        {
            "name": "Swarat Chaudhuri",
            "research_interests": "AI, Programming Languages",
            "contact_email": "swarat@utexas.edu",
            "url": "https://www.cs.utexas.edu/people/swarat-chaudhuri"
        }
    ],
    "labs": [
        {
            "name": "Institute for Foundations of Machine Learning",
            "focus": "Foundational tools for AI innovation",
            "url": "https://www.ifml.institute/"
        }
    ]
}
"""

@app.route("/", methods=["GET"])
def index():
    """
    Parse the JSON and render a template showing 
    each professor/lab as clickable buttons.
    """
    data = json.loads(json_data)

    # 'data' is now a Python dict: 
    # { "professors": [...], "labs": [...] }

    return render_template("index.html", data=data)


@app.route("/select", methods=["POST"])
def select():
    """
    Handle button click. We read the hidden fields posted
    and display them.
    """
    prof_name = request.form.get("prof_name")
    prof_research = request.form.get("prof_research")
    prof_email = request.form.get("prof_email")
    prof_url = request.form.get("prof_url")

    lab_name = request.form.get("lab_name")
    lab_focus = request.form.get("lab_focus")
    lab_url = request.form.get("lab_url")

    if prof_name:
        # The user selected a professor
        return f"""
            <h2>Selected Professor</h2>
            <p><strong>Name:</strong> {prof_name}</p>
            <p><strong>Research Interests:</strong> {prof_research}</p>
            <p><strong>Email:</strong> {prof_email}</p>
            <p><strong>URL:</strong> <a href='{prof_url}' target='_blank'>{prof_url}</a></p>
            <br><a href="/">Back to Home</a>
        """

    elif lab_name:
        # The user selected a lab
        return f"""
            <h2>Selected Lab</h2>
            <p><strong>Name:</strong> {lab_name}</p>
            <p><strong>Focus:</strong> {lab_focus}</p>
            <p><strong>URL:</strong> <a href='{lab_url}' target='_blank'>{lab_url}</a></p>
            <br><a href="/">Back to Home</a>
        """

    else:
        # Fallback
        return "<h2>No selection received.</h2><br><a href='/'>Back to Home</a>"


if __name__ == "__main__":
    app.run(debug=True)
