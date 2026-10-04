# Running guide

Use this guide to install, launch, and troubleshoot Research Studio. Commands are written for Windows PowerShell; Linux and macOS commands are included at the end.

## Contents

- [Requirements](#requirements)
- [Windows setup](#windows-setup)
- [Launch the dashboard](#launch-the-dashboard)
- [Run a research query](#run-a-research-query)
- [Use the dashboard](#use-the-dashboard)
- [Troubleshooting](#troubleshooting)
- [Linux and macOS](#linux-and-macos)

## Requirements

- Python 3.10 or newer
- An internet connection for web search, fetching pages, and the first model download
- PowerShell on Windows, or a terminal on Linux/macOS

## Windows setup

Open PowerShell in the project folder (the folder containing `requirements.txt`) and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

When activated, your prompt should show `(.venv)`. To confirm the selected Python:

```powershell
python --version
python -m pip --version
```

### If PowerShell blocks activation

Allow script activation only in the current PowerShell process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Alternatively, call the environment's executables directly without activating it:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\streamlit.exe run streamlit_app.py
```

## Launch the dashboard

With the project environment activated:

```powershell
streamlit run streamlit_app.py
```

Streamlit prints a local address in the terminal. Open that address in your browser; the default is [http://localhost:8501](http://localhost:8501).

To use another port:

```powershell
streamlit run streamlit_app.py --server.port 8502
```

Keep the terminal window open while using the dashboard. Press **Ctrl+C** in that window to stop the server.

## Run a research query

### In the dashboard

1. Enter a question or pick one of the suggested prompts.
2. Adjust search depth and summary settings in the sidebar if needed.
3. Select **Research this question**.
4. Review the summary, source links, and ranked passages.
5. Download the report as Markdown when you want a local copy.

### From PowerShell

```powershell
python app.py "What causes urban heat islands and how can cities reduce them?"
```

The first research query may take longer because the embedding model is downloaded and initialized.

## Use the dashboard

- **Web pages to search** controls how many search results the agent checks.
- **Passages per page** controls how much text is collected from each result.
- **Passages to show** controls the number of top-ranked passages.
- **Summary length** controls how many extractive summary sentences are selected.
- **Minimum match score** filters out passages below the selected semantic similarity score.
- **Overview** gives a brief and source list; **Sources** lets you inspect and sort individual passages.
- **Your workspace** lets you reopen or clear reports from the current browser session.

## Troubleshooting

<details>
<summary><strong><code>streamlit</code> is not recognized</strong></summary>

Confirm that `.venv` is activated. If it is, run:

```powershell
python -m streamlit run streamlit_app.py
```

Or run the environment executable directly:

```powershell
.\.venv\Scripts\streamlit.exe run streamlit_app.py
```

</details>

<details>
<summary><strong>Packages are missing or imports fail</strong></summary>

Check that PowerShell is using the project environment, then reinstall the declared dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

</details>

<details>
<summary><strong>The first search is slow</strong></summary>

The agent downloads and initializes its sentence-transformer model the first time it runs. Keep the terminal open and wait for the model download to finish. Later searches reuse the initialized model while the app process remains running.

</details>

<details>
<summary><strong>Search returns few or no passages</strong></summary>

Check your internet connection and try a more specific question. Some sites block automated page requests, and search results can change or become unavailable. Try increasing **Web pages to search** or lowering **Minimum match score**.

</details>

<details>
<summary><strong>Port 8501 is already in use</strong></summary>

Start the dashboard on another port:

```powershell
streamlit run streamlit_app.py --server.port 8502
```

</details>

## Linux and macOS

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

For the CLI:

```bash
python app.py "What causes urban heat islands and how can cities reduce them?"
```

## Stop the dashboard

Focus the terminal running Streamlit and press **Ctrl+C**. The browser page will no longer be connected to the app.
