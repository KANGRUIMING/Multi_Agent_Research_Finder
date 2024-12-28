# src/ai_research_position/satisfaction_handler.py

def assess_satisfaction(chat_output, professors):
    """
    Assess the user's satisfaction based on chat output.

    Parameters:
    - chat_output (dict): Output from the chat_task
    - professors (list): List of professors from research_task

    Returns:
    - dict: Action to take next
      - If satisfied, contains 'satisfied': True and 'chosen_professor': professor dict
      - If not satisfied, contains 'satisfied': False and 'new_topic'/'new_university' etc.
    """
    satisfaction = chat_output.get('satisfaction', '').strip().lower()
    additional_info = chat_output.get('additional_info', '').strip()
    chosen_professor = chat_output.get('chosen_professor', '').strip()

    if satisfaction in ['yes', 'y']:
        if chosen_professor:
            # Find the professor in the list
            for prof in professors:
                if prof['name'].lower() == chosen_professor.lower():
                    return {'satisfied': True, 'chosen_professor': prof}
            # Professor not found
            print(f"Professor '{chosen_professor}' not found in the research results.")
            return {'satisfied': False, 'error': 'Professor not found'}
        else:
            # Ask the user to choose a professor
            return {'satisfied': False, 'action': 'choose_professor'}
    elif satisfaction in ['no', 'n']:
        if additional_info:
            # Assume user provides new topic or university
            # For simplicity, we'll ask the user to specify
            return {'satisfied': False, 'update_info': additional_info}
        else:
            # Prompt the user to provide more details
            return {'satisfied': False, 'action': 'ask_more_details'}
    else:
        # Unrecognized input
        print("Unrecognized satisfaction response.")
        return {'satisfied': False, 'error': 'Unrecognized response'}
