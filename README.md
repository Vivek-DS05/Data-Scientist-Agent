# 📊 Data Scientist Agent

An intelligent, multi-agent conversational assistant for data science powered by **Mistral AI**, **LangChain / deepagents**, **FastAPI**, and **Streamlit**.

Upload any CSV dataset, ask questions in natural English, and receive automated exploratory data analysis, data cleaning, publication-quality visualizations, and plain-English business insights.

---

## 🌟 Key Features

- **Multi-Agent Architecture**: Dedicated specialist sub-agents collaborate to profile data, generate code, produce charts, and craft narrative explanations.
- **Natural Language Data Analysis**: Ask questions in plain English—no manual SQL or pandas scripting required.
- **Dynamic Chart Generation**: Automatically generates and renders publication-ready charts using Matplotlib and Seaborn.
- **Automated Data Cleaning**: Detects missing values, anomalies, and duplicates with clear explanations of transformations.
- **Modular Skills System**: Procedural knowledge guides (`skills/`) allow sub-agents to follow best practices for EDA, cleaning, visualization, and insight generation.
- **Full Execution Transparency**: View generated Python code alongside results and plots directly within the chat interface.

---

## 🏗️ Architecture

The system uses a hierarchical multi-agent workflow orchestrated by `deepagents`:

```
                           ┌────────────────────────┐
                           │   Streamlit Web UI     │
                           │   (frontend/app.py)    │
                           └───────────┬────────────┘
                                       │ HTTP
                           ┌───────────▼────────────┐
                           │      FastAPI API       │
                           │   (backend/main.py)    │
                           └───────────┬────────────┘
                                       │
                      ┌────────────────▼────────────────┐
                      │    Orchestrator Agent           │
                      │    (backend/agent.py)           │
                      └────────────────┬────────────────┘
                                       │
             ┌─────────────────────────┼─────────────────────────┐
             │                         │                         │
┌────────────▼───────────┐ ┌───────────▼───────────┐ ┌───────────▼───────────┐
│     Data Analyst       │ │      Visualizer       │ │    Insight Writer     │
│   (EDA, Stats, Clean)  │ │ (Matplotlib / Seaborn)│ │   (Plain English)     │
└────────────┬───────────┘ └───────────┬───────────┘ └───────────┬───────────┘
             │                         │                         │
             └─────────────────────────┼─────────────────────────┘
                                       │
                      ┌────────────────▼────────────────┐
                      │   Tools & Skills Ecosystem      │
                      │   • run_python_code             │
                      │   • read_skill / list_skills    │
                      │   • skills/ (eda, cleaning, ...)│
                      └─────────────────────────────────┘
```

### Specialized Agents:
1. **Orchestrator (`backend/agent.py`)**: Understands user intent, coordinates execution across sub-agents, and synthesizes final responses.
2. **Data Analyst (`backend/subagents.py`)**: Writes and executes Pandas/NumPy code for statistical summaries, correlations, and data cleaning.
3. **Visualizer (`backend/subagents.py`)**: Creates clean, informative charts tailored to the data distribution.
4. **Insight Writer (`backend/subagents.py`)**: Translates technical outputs and charts into actionable, non-technical takeaways.

---

## 📁 Repository Structure

```
data-agent/
├── backend/
│   ├── agent.py          # Orchestrator agent & LLM setup
│   ├── main.py           # FastAPI backend server
│   ├── subagents.py      # Specialized sub-agents (analyst, visualizer, insights)
│   └── tools.py          # Sandboxed Python execution & skill tools
├── data/
│   ├── plots/            # Generated chart images (git-ignored)
│   └── uploads/          # Uploaded CSV files (git-ignored)
├── frontend/
│   └── app.py            # Streamlit interactive chat interface
├── skills/
│   ├── cleaning/         # Data cleaning guidelines & best practices
│   ├── eda/              # Exploratory data analysis guidelines
│   ├── insights/         # Plain-English translation rules
│   └── plotting/         # Data visualization & chart selection rules
├── .env.example          # Template for environment variables
├── .gitignore            # Git exclusion rules
├── pyproject.toml        # Project metadata & dependencies
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10+ (or 3.14 via `uv`)
- A [Mistral AI API Key](https://console.mistral.ai/)

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/data-agent.git
cd data-agent
```

### 3. Set Up Virtual Environment

```bash
# Using standard venv
python -m venv .venv

# On Linux / macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy the sample environment file:

```bash
cp .env.example .env
```

Open `.env` and add your Mistral API key:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
LLM_MODEL=mistral-small-latest
```

---

## 🖥️ Running the Application

Launch the backend API and the frontend UI in separate terminal windows:

### Terminal 1: Backend API (FastAPI)

```bash
uvicorn backend.main:app --reload --port 8000
```
*API docs will be available at: `http://localhost:8000/docs`*

### Terminal 2: Frontend UI (Streamlit)

```bash
streamlit run frontend/app.py
```
*The web interface will open automatically at: `http://localhost:8501`*

---

## 💬 Example Queries

Once you upload a CSV file in the sidebar, try asking questions like:

- **Overview & Profiling:**
  - *"What does this dataset look like?"*
  - *"Which columns have missing values, and how many?"*
- **Statistical Analysis:**
  - *"Is there a correlation between price and customer rating?"*
  - *"Find the top 5 categories by total revenue."*
- **Visualizations:**
  - *"Plot the distribution of the age column."*
  - *"Show a correlation heatmap for all numerical features."*
- **Data Cleaning:**
  - *"Clean the dataset by handling missing values and explain what was changed."*

---

## 🔒 Security & Safe Execution

- **Environment Variables**: Never commit your `.env` file containing secrets. `.env` is already configured in `.gitignore`.
- **Code Execution**: The `run_python_code` tool executes generated code in a local environment. When deploying to production or multi-tenant setups, run code execution inside isolated containers (e.g. Docker, gVisor, or E2B).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).