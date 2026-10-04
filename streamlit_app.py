from datetime import datetime
import uuid

import streamlit as st

from research_agent.agent import ResearchAgent

EXAMPLE_QUERIES = [
    ("AI in medicine", "How is AI changing medical diagnosis?"),
    ("Heat-resilient cities", "What makes a city resilient to extreme heat?"),
    ("Grid-scale batteries", "Which materials are promising for grid-scale batteries?"),
]
HISTORY_KEY = "research_history"
MAX_HISTORY = 20

st.set_page_config(
    page_title="Research studio",
    page_icon=":material/travel_explore:",
    layout="wide",
)


@st.cache_resource(show_spinner=False)
def get_agent() -> ResearchAgent:
    return ResearchAgent()


def set_example_query(query: str) -> None:
    st.session_state["research_query"] = query


def clear_history() -> None:
    st.session_state[HISTORY_KEY] = []
    st.session_state.pop("report_picker", None)


st.session_state.setdefault(HISTORY_KEY, [])

with st.sidebar:
    st.title("Research studio", anchor=False)
    st.caption("A focused workspace for web research.")
    st.subheader("Search settings")
    max_results = st.slider("Web pages to search", min_value=3, max_value=10, value=6)
    passages_per_page = st.slider("Passages per page", min_value=1, max_value=6, value=4)
    top_passages = st.slider("Passages to show", min_value=3, max_value=8, value=5)
    summary_sentences = st.slider("Summary length", min_value=2, max_value=6, value=3)
    min_score = st.slider(
        "Minimum match score",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
        help="Hide passages with a lower semantic similarity score.",
    )

st.title("Research workspace", icon=":material/travel_explore:")
st.write("Ask a question. Get a concise brief backed by relevant web sources.")

st.caption("Need a starting point?")
example_columns = st.columns(3)
for index, (column, (label, example)) in enumerate(zip(example_columns, EXAMPLE_QUERIES)):
    with column:
        st.button(
            label,
            key=f"example_{index}",
            on_click=set_example_query,
            args=(example,),
            width="stretch",
            help=example,
        )

with st.container(border=True):
    st.subheader("Start a research brief", anchor=False)
    with st.form("research_form", border=False):
        query = st.text_input(
            "Research question",
            key="research_query",
            placeholder="e.g. How can cities reduce the urban heat island effect?",
        )
        submitted = st.form_submit_button(
            "Research this question",
            type="primary",
            icon=":material/search:",
            width="stretch",
        )

if submitted:
    if not query.strip():
        st.warning("Enter a research question to get started.")
    else:
        try:
            with st.status("Researching the web…", expanded=True) as status:
                st.write("Finding pages, ranking useful passages, and drafting your brief.")
                result = get_agent().run(
                    query.strip(),
                    max_results=max_results,
                    passages_per_page=passages_per_page,
                    top_passages=top_passages,
                    summary_sentences=summary_sentences,
                )
                status.update(
                    label="Research complete",
                    state="complete",
                    expanded=False,
                )

            report = {
                "id": uuid.uuid4().hex,
                "query": query.strip(),
                "created_at": datetime.now().astimezone().strftime("%b %d, %Y at %I:%M %p"),
                "result": result,
            }
            st.session_state[HISTORY_KEY] = (
                [report] + st.session_state[HISTORY_KEY]
            )[:MAX_HISTORY]
            st.session_state["report_picker"] = report["id"]
        except Exception as error:
            st.error(f"Research could not be completed: {error}")

with st.sidebar:
    st.space("medium")
    st.subheader("Your workspace")
    st.caption(f"{len(st.session_state[HISTORY_KEY])} saved reports in this session")
    st.button(
        "Clear report history",
        icon=":material/delete:",
        disabled=not st.session_state[HISTORY_KEY],
        on_click=clear_history,
        width="stretch",
    )
    st.space("large")
    st.caption("Research results are saved only for this browser session.")

history = st.session_state[HISTORY_KEY]
if not history:
    with st.container(border=True):
        st.subheader("Your research brief will appear here", anchor=False)
        st.write(
            "Submit a question to search the web, compare relevant passages, "
            "and collect source links in one place."
        )
else:
    st.space("medium")
    st.subheader("Research report", anchor=False)
    report_ids = [report["id"] for report in history]
    selected_id = st.selectbox(
        "Choose a saved report",
        options=report_ids,
        format_func=lambda report_id: next(
            report["query"] for report in history if report["id"] == report_id
        ),
        key="report_picker",
    )
    report = next(item for item in history if item["id"] == selected_id)
    result = report["result"]
    passages = result["passages"]
    filtered_passages = [
        passage for passage in passages if passage["score"] >= min_score
    ]
    unique_sources = {passage["url"] for passage in passages}

    st.caption(f"Created {report['created_at']}")
    with st.container(horizontal=True):
        st.metric("Sources found", len(unique_sources), border=True)
        st.metric("Relevant passages", len(filtered_passages), border=True)
        st.metric("Research time", f"{result['time']:.1f}s", border=True)

    report_markdown = (
        f"# Research brief\n\n"
        f"**Question:** {report['query']}\n\n"
        f"**Created:** {report['created_at']}\n\n"
        f"## Summary\n\n{result['summary']}\n\n"
        "## Sources and relevant passages\n\n"
        + "\n\n".join(
            f"### {index}. {passage['url']} — match {passage['score']:.3f}\n\n"
            f"{passage['passage']}"
            for index, passage in enumerate(passages, start=1)
        )
    )
    st.download_button(
        "Download report",
        data=report_markdown,
        file_name="research-brief.md",
        mime="text/markdown",
        icon=":material/download:",
    )

    view = st.segmented_control(
        "Report view",
        options=["Overview", "Sources"],
        default="Overview",
        key="report_view",
    )

    if view == "Sources":
        st.subheader("Relevant passages", anchor=False)
        sort_by = st.selectbox(
            "Sort sources",
            options=["Best match", "Source URL"],
            label_visibility="collapsed",
        )
        if sort_by == "Source URL":
            filtered_passages.sort(key=lambda passage: passage["url"].lower())
        else:
            filtered_passages.sort(key=lambda passage: passage["score"], reverse=True)

        if not filtered_passages:
            st.info("No passages meet this match-score filter. Lower the minimum score in the sidebar.")
        else:
            for index, passage in enumerate(filtered_passages, start=1):
                with st.container(border=True):
                    st.badge(f"Match {passage['score']:.0%}", color="blue")
                    st.markdown(f"**Passage {index}**")
                    st.text(passage["passage"])
                    st.link_button(
                        passage["url"],
                        passage["url"],
                        icon=":material/open_in_new:",
                    )
    else:
        summary_column, sources_column = st.columns([1.5, 1])
        with summary_column:
            with st.container(border=True):
                st.subheader("Executive summary", anchor=False)
                if result["summary"]:
                    st.text(result["summary"])
                else:
                    st.info("No summary could be generated from the retrieved passages.")
        with sources_column:
            with st.container(border=True):
                st.subheader("Top sources", anchor=False)
                if not filtered_passages:
                    st.info("No passages meet this match-score filter. Lower the minimum score in the sidebar.")
                else:
                    shown_sources: set[str] = set()
                    for passage in filtered_passages:
                        if passage["url"] in shown_sources:
                            continue
                        shown_sources.add(passage["url"])
                        st.link_button(
                            passage["url"],
                            passage["url"],
                            icon=":material/open_in_new:",
                            width="stretch",
                        )
