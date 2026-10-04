import re
import time
import urllib.parse
from typing import Any

import numpy as np
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from sentence_transformers import SentenceTransformer

SEARCH_RESULTS = 6
PASSAGES_PER_PAGE = 4
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_PASSAGES = 5
SUMMARY_SENTENCES = 3
TIMEOUT = 8


def unwrap_ddg(url: str) -> str:
    """Resolve DuckDuckGo redirect wrappers back to the real URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        if "duckduckgo.com" in parsed.netloc:
            qs = urllib.parse.parse_qs(parsed.query)
            uddg = qs.get("uddg")
            if uddg:
                return urllib.parse.unquote(uddg[0])
    except Exception:
        pass
    return url


def search_web(query: str, max_results: int = SEARCH_RESULTS) -> list[str]:
    """Return a list of web URLs matching the search query."""
    urls: list[str] = []
    with DDGS() as ddgs:
        for result in ddgs.text(query, max_results=max_results):
            url = result.get("href") or result.get("url")
            if not url:
                continue
            urls.append(unwrap_ddg(url))
    return urls


def fetch_text(url: str, timeout: int = TIMEOUT) -> str:
    """Fetch HTML from a URL and return cleaned text content."""
    headers = {"User-Agent": "Mozilla/5.0 (research-agent)"}
    try:
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        if response.status_code != 200:
            return ""

        content_type = response.headers.get("content-type", "")
        if "html" not in content_type.lower():
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript", "header", "footer", "svg", "iframe", "nav", "aside"]):
            tag.extract()

        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = " ".join(part for part in paragraphs if part)

        if text.strip():
            return re.sub(r"\s+", " ", text).strip()

        meta = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta and meta.get("content"):
            return meta["content"].strip()

        if soup.title and soup.title.string:
            return soup.title.string.strip()
    except Exception:
        return ""
    return ""


def chunk_passages(text: str, max_words: int = 120) -> list[str]:
    """Split long text into smaller passages."""
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        chunk = words[start : start + max_words]
        chunks.append(" ".join(chunk))
        start += max_words
    return chunks


def split_sentences(text: str) -> list[str]:
    """Split text into sentences with a simple rule-based splitter."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if part.strip()]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class ResearchAgent:
    """A lightweight research agent that searches the web, retrieves passages, and summarizes them."""

    def __init__(self, embed_model: str = EMBEDDING_MODEL):
        self.embedder = SentenceTransformer(embed_model)

    def run(
        self,
        query: str,
        max_results: int = SEARCH_RESULTS,
        passages_per_page: int = PASSAGES_PER_PAGE,
        top_passages: int = TOP_PASSAGES,
        summary_sentences: int = SUMMARY_SENTENCES,
    ) -> dict[str, Any]:
        start = time.time()
        urls = search_web(query, max_results=max_results)

        documents: list[dict[str, str]] = []
        for url in urls:
            text = fetch_text(url)
            if not text:
                continue

            for chunk in chunk_passages(text, max_words=120)[:passages_per_page]:
                documents.append({"url": url, "passage": chunk})

        if not documents:
            return {
                "query": query,
                "passages": [],
                "summary": "No relevant passages were found for this query.",
                "time": time.time() - start,
            }

        passage_texts = [doc["passage"] for doc in documents]
        passage_embeddings = self.embedder.encode(passage_texts, convert_to_numpy=True, show_progress_bar=False)
        query_embedding = self.embedder.encode([query], convert_to_numpy=True)[0]

        sims = [cosine_similarity(embedding, query_embedding) for embedding in passage_embeddings]
        top_idx = np.argsort(sims)[::-1][:top_passages]
        ranked_passages = [
            {
                "url": documents[i]["url"],
                "passage": documents[i]["passage"],
                "score": float(sims[i]),
            }
            for i in top_idx
        ]

        sentences: list[dict[str, str]] = []
        for passage in ranked_passages:
            for sentence in split_sentences(passage["passage"]):
                sentences.append({"sentence": sentence, "url": passage["url"]})

        if not sentences:
            summary = "No summary could be generated from the retrieved passages."
        else:
            sentence_texts = [sentence["sentence"] for sentence in sentences]
            sentence_embeddings = self.embedder.encode(sentence_texts, convert_to_numpy=True, show_progress_bar=False)
            sentence_scores = [cosine_similarity(embedding, query_embedding) for embedding in sentence_embeddings]
            selected_indexes = np.argsort(sentence_scores)[::-1][:summary_sentences]
            chosen = [sentences[i] for i in selected_indexes]

            seen: set[str] = set()
            summary_lines: list[str] = []
            for item in chosen:
                key = item["sentence"].lower()[:80]
                if key in seen:
                    continue
                seen.add(key)
                summary_lines.append(f"{item['sentence']} (Source: {item['url']})")
            summary = " ".join(summary_lines)

        return {
            "query": query,
            "passages": ranked_passages,
            "summary": summary,
            "time": time.time() - start,
        }


if __name__ == "__main__":
    agent = ResearchAgent()
    result = agent.run("What causes urban heat islands and how can cities reduce them?")
    print(result["summary"])
