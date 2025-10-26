# Support Chat for Survivors

This project provides a minimal full-stack application that offers a supportive chat experience for women experiencing domestic or financial abuse. The interface delivers empathetic, safety-first responses, highlights trusted resources, and performs lightweight keyword analysis so advocates can monitor urgent situations.

> **Important:** This application cannot replace professional advice or emergency services. Always encourage users in immediate danger to contact local emergency services (for example, 911 in the United States) or reach out to a trusted person nearby.

## Features

- **Supportive chat bot** that stores conversations securely in a local SQLite database and returns trauma-informed responses.
- **Resource directory** with international crisis lines, financial safety guidance, and live chat links.
- **Automated analysis** that flags high-risk keywords and summarizes message counts to guide follow-up by trained advocates.
- **Front-end dashboard** with a calming interface, quick “start new conversation” button, and reminders about device safety.

## Project structure

```
.
├── backend
│   ├── app.py             # Flask application and REST API endpoints
│   ├── database.py        # SQLAlchemy engine, session, and base class
│   ├── models.py          # Conversation and Message ORM models
│   ├── support.py         # Risk assessment logic and resource catalog
│   └── __init__.py
├── frontend
│   ├── index.html         # Chat interface, resource list, and insights panels
│   ├── styles.css         # Styling for a calm and accessible experience
│   └── app.js             # Browser logic for chat, analysis, and resources
├── requirements.txt       # Python dependencies for the backend API
└── README.md
```

## Getting started

### 1. Set up the backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m backend.app
```

The Flask API runs on `http://localhost:5000`. A SQLite database file named `chatbot.db` is created in the project root.

### 2. Launch the frontend

Use any static file server to host the contents of the `frontend` directory. For example:

```bash
python -m http.server --directory frontend 5173
```

Then open `http://localhost:5173` in a browser. The JavaScript client communicates with the Flask API running on port 5000.

### 3. Run a conversation

1. Enter a message describing the situation.
2. Review the bot’s supportive response and the suggested resources beneath the chat window.
3. Inspect the “Conversation Insights” panel to see keyword flags and overall risk level.
4. Click **Start New Conversation** to reset the view without deleting stored data.

## Data and privacy considerations

- The application stores conversations locally only. Deployments should use encrypted storage and restrict database access to trained staff.
- If you plan to collect identifiable information, ensure your deployment complies with relevant privacy laws (HIPAA, GDPR, etc.).
- Consider adding an auto-expire policy or secure export mechanism depending on organizational requirements.
- Clearly communicate to end users how their data will be stored, analyzed, and used.

## Next steps

- Integrate with a secure authentication layer so only trained advocates can access conversation analytics.
- Expand the resource list with localized services for the regions you serve.
- Replace the keyword matcher with an audited NLP model that is tuned for trauma-informed language and evaluated for bias.
- Add proactive safety features such as “quick exit” buttons or configurable disguising of the page title.

Please ensure that any enhancements continue to prioritize survivor safety, privacy, and consent.
