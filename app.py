import argparse

from research_agent.agent import ResearchAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a research agent over web search results.")
    parser.add_argument("query", help="Research question to investigate.")
    parser.add_argument("--max-results", type=int, default=6, help="Number of search results to inspect.")
    parser.add_argument("--passages-per-page", type=int, default=4, help="Number of passages to pull from each page.")
    parser.add_argument("--top-passages", type=int, default=5, help="How many relevant passages to include.")
    parser.add_argument("--summary-sentences", type=int, default=3, help="How many sentences to include in the summary.")
    args = parser.parse_args()

    agent = ResearchAgent()
    result = agent.run(
        args.query,
        max_results=args.max_results,
        passages_per_page=args.passages_per_page,
        top_passages=args.top_passages,
        summary_sentences=args.summary_sentences,
    )

    print(f"Query: {result['query']}")
    print(f"Search completed in {result['time']:.2f} seconds")
    print("\nSummary:")
    print(result["summary"])
    print("\nTop passages:")
    for i, passage in enumerate(result["passages"], 1):
        print(f"\n{i}. Score={passage['score']:.3f} | {passage['url']}")
        print(passage["passage"][:220] + ("..." if len(passage["passage"]) > 220 else ""))


if __name__ == "__main__":
    main()
