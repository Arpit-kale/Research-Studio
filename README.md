<div align="center">

# Research Studio

### Turn a question into a source-backed research brief.

Search the web, rank useful passages by meaning, and review the sources in a clean interactive dashboard.

[Get started](#-get-started) · [Run the dashboard](#-launch-the-dashboard) · [How it works](#-how-it-works) · [Running guide](RUNNING_GUIDE.md) · [MIT license](LICENSE)

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-37C9A5.svg)

</div>

---

## ✨ What you can do

| Feature | Description |
| --- | --- |
| **Ask in plain language** | Start with your own question or choose a quick-start prompt. |
| **Search the web** | Find relevant pages with DuckDuckGo and retrieve their text. |
| **Rank by meaning** | Compare passages to your question using sentence embeddings. |
| **Review the evidence** | Explore source links, match scores, and relevant passages. |
| **Tune your research** | Adjust search depth, summary length, and the match-score filter. |
| **Keep and export briefs** | Revisit reports during your browser session or download a Markdown copy. |

## 🚀 Get started

### 1. Open the project folder

Open PowerShell in the folder containing `requirements.txt` and `streamlit_app.py`.

### 2. Create an environment and install dependencies

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> **PowerShell activation blocked?** Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. This changes the policy only for the current PowerShell window.

### 3. Launch the dashboard

```powershell
streamlit run streamlit_app.py
```

Open the local URL printed in the terminal (usually **http://localhost:8501**).

<details>
<summary><strong>Prefer the command line?</strong></summary>

```powershell
python app.py "What causes urban heat islands and how can cities reduce them?"
```

</details>

## 🧭 How to use the dashboard

1. Choose a suggested research prompt or type your own question.
2. Optionally adjust search settings in the sidebar.
3. Select **Research this question** and wait for the report.
4. Read the summary, open source links, and inspect passages in the **Sources** view.
5. Use the minimum match score to filter weaker matches.
6. Select **Download report** to save the brief as a Markdown file.

## 🔎 How it works

```text
Question → Web search → Page extraction → Passage chunking
         → Semantic ranking → Source-linked summary
```

The agent uses DuckDuckGo for discovery, Beautiful Soup and Requests to extract page text, and `sentence-transformers/all-MiniLM-L6-v2` to rank passages by cosine similarity. The summary is extractive: it selects relevant sentences from retrieved passages rather than generating new claims.

## 🗂️ Project layout

```text
.
├── app.py                  # Command-line entry point
├── streamlit_app.py        # Interactive research dashboard
├── research_agent/
│   └── agent.py            # Search, retrieval, ranking, and summary logic
├── .streamlit/
│   └── config.toml         # Dashboard theme
├── requirements.txt
├── RUNNING_GUIDE.md        # Detailed setup and troubleshooting
└── LICENSE
```

## 💡 First-run notes

- The first research run downloads the sentence-transformer model; allow a little extra time and keep an internet connection available.
- Search results and page availability depend on DuckDuckGo and the websites being reachable.
- Reports are stored in Streamlit session state. They are session-only, not a permanent database; download a report if you want to keep it.
- Treat retrieved material as research leads and verify important claims against the linked sources.

## 📚 More information

- [Detailed running guide](RUNNING_GUIDE.md)
- [MIT license](LICENSE)
- [Article that inspired this project](https://amanxai.com/2025/11/11/build-an-ai-agent-to-automate-your-research/)

<div align="center">

Made for curious minds · Built with Python and Streamlit

</div>
