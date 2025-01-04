```mermaid
flowchart TB
    A["User Inputs:<br>- University<br>- Research Interest<br>- Resume"]
    --> B["Research Agent<br>(Find Professors/Labs +<br>Contact Info)"]
    B --> C["User Chooses<br>Professor/Lab"]
    C --> D["Deeper Research Agent<br>(Additional Info)"]
    D --> E["Cover Letter Agent<br>(Uses Resume to Craft Letter)"]
