# LangGraph Essay Evaluation System

A real-time AI-powered essay evaluation system built with **LangGraph**, **FastAPI**, and **React**. This application automates the process of generating essay topics, collecting user input, and providing multi-dimensional feedback (Clarity, Depth, Vocabulary) using LLMs.

## 🚀 Features

-   **Interactive Workflow**: Visualized using optimized React Flow nodes.
-   **Real-time Feedback**: Streams evaluation steps and scores from the backend.
-   **Multi-Agent Evaluation**:
    -   **Clarity Agent**: Checks flow and coherence.
    -   **Depth Agent**: Analyzes the depth of arguments and evidence.
    -   **Vocabulary Agent**: Evaluates language precision.
-   **Automated Scoring**: Aggregates scores and determines pass/fail status.
-   **Detailed Feedback**: Generates actionable improvement tips for low scores.

## 🛠️ Tech Stack

-   **Frontend**: React, Vite, React Flow, Tailwind CSS, Lucide React
-   **Backend**: FastAPI, LangGraph, LangChain, Google Gemini (LLM)
-   **State Management**: SSE (Server-Sent Events) for real-time updates

## 📂 Project Structure

```bash
├── backend/
│   ├── main.py          # FastAPI entry point
│   ├── graph.py         # LangGraph workflow definition
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main UI and React Flow logic
│   │   └── components/  # Custom nodes and modals
│   └── package.json     # Frontend dependencies
└── README.md
```

## ⚡ Setup & Installation

### Prerequisites
-   Python 3.10+
-   Node.js 18+
-   Google Gemini API Key

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root or `backend` directory:
```env
GOOGLE_API_KEY=your_api_key_here
```

Run the backend server:
```bash
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

## 🔄 Usage

1.  Click **Start Workflow** to generate a UPSC-standard essay topic.
2.  Write your essay in the modal provided.
3.  Click **Submit**. The system will visualize the evaluation process in real-time.
4.  View your scores for Clarity, Depth, and Vocabulary.
5.  If the score is below 10/15, receive detailed feedback and try again.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.
