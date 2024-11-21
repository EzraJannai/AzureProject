from flask import Flask, request, render_template, send_file
import requests
import tempfile
import os

app = Flask(__name__)

def llm_convert_ical_to_text(ical_content):
    # Use LLM to convert ICAL content to human-readable text
    url = "http://localhost:11434/api/generate"
    prompt = f"""You are an AI that converts iCalendar (.ics) files into a human-readable event list. You convert ICAL content into a structured, readable list of events like this:
    
    Example ICAL content:
    BEGIN:VEVENT\nSUMMARY:Team Meeting\nDTSTART:20230515T090000\nDTEND:20230515T100000\nEND:VEVENT

    Example Output:
    Event: Team Meeting, Start: 2023-05-15 09:00, End: 2023-05-15 10:00
    
    Now the actual ICAL content.
    ICAL content:
    {ical_content}

    Ouput:
    """
    
    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "Error processing ICAL conversion"
    except Exception as e:
        return f"Error: {str(e)}"

def llm_integrate_notes_with_calendar(notes, calendar_text):
    # AI agent to integrate user notes into the calendar text
    url = "http://localhost:11434/api/generate"
    prompt = f"""You are an AI tasked with integrating user notes into an existing calendar. 
    Please provide an updated list of calendar events with the new notes logically added and adjusted where appropriate.

    Example:
    Original Events:
    Event: Team Meeting, Start: 2023-05-15 09:00, End: 2023-05-15 10:00

    Notes: Add a follow-up meeting after Team Meeting.

    Updated Events:
    Event: Team Meeting, Start: 2023-05-15 09:00, End: 2023-05-15 10:00
    Event: Follow-up Meeting, Start: 2023-05-15 10:30, End: 2023-05-15 11:00
    
    Now the actual data:
    Original events:
    {calendar_text}
    Notes:
    {notes}

    Updated Events:
    """

    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "Error processing integration"
    except Exception as e:
        return f"Error: {str(e)}"

def llm_generate_ical_from_text(calendar_text):
    # Use LLM to convert updated text back to ICAL format
    url = "http://localhost:11434/api/generate"
    prompt = f"""You are an AI that converts human-readable calendar event lists back into iCalendar (.ics) format.
    
    The following is an example list of calendar events:
    Events: Team Meeting, Start: 2023-05-15 09:00, End: 2023-05-15 10:00

    Ouput:
    BEGIN:VEVENT\nSUMMARY:Team Meeting\nDTSTART:20230515T090000\nDTEND:20230515T100000\nEND:VEVENT

    Now the actual data
    Events:
    {calendar_text}

    ICAL format of events:"""
    
    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "Error generating ICAL"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    calendar_text = None
    updated_calendar_text = None
    updated_ical = None
    if request.method == 'POST':
        if 'ical_file' in request.files:
            ical_file = request.files['ical_file']
            ical_content = ical_file.read().decode('utf-8')
            calendar_text = llm_convert_ical_to_text(ical_content)
        
        if 'notes' in request.form and calendar_text:
            notes = request.form['notes']
            updated_calendar_text = llm_integrate_notes_with_calendar(notes, calendar_text)
            updated_ical = llm_generate_ical_from_text(updated_calendar_text)
            
            # Save ICAL to a temporary file to allow for download
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ics')
            with open(temp_file.name, 'w') as f:
                f.write(updated_ical)
            temp_file_path = temp_file.name

            return render_template('index.html', calendar_text=calendar_text, updated_calendar_text=updated_calendar_text, ical_download_path=temp_file_path)
    
    return render_template('index.html', calendar_text=calendar_text, updated_calendar_text=updated_calendar_text)

@app.route('/download_ical', methods=['GET'])
def download_ical():
    ical_path = request.args.get('ical_path')
    if ical_path and os.path.exists(ical_path):
        return send_file(ical_path, as_attachment=True, download_name='updated_calendar.ics')
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)

# HTML Template (index.html)
# Save this in a templates directory as index.html

"""

"""
