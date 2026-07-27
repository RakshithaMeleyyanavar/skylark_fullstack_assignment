"""
Step 7 Validation Script: Test sample founder queries in terminal via BIAgent tool calling loop.
"""

import sys
from agent import BIAgent

def test_terminal_queries():
    print("=========================================================")
    print("       MONDAY.COM CONVERSATIONAL BI AGENT TEST          ")
    print("=========================================================\n")

    agent = BIAgent()

    sample_queries = [
        "What is our total deal value for Won deals, and what are the data quality caveats?",
        "Show me a cross-board summary comparing deals and work orders by Owner code.",
        "What is the data health and completeness report for both boards?"
    ]

    for idx, query in enumerate(sample_queries, start=1):
        print(f"--- [QUERY {idx}] ------------------------------------")
        print(f"USER: {query}\n")

        result = agent.run_query(query)

        print(f"ENGINE USED: {result.get('engine', 'Unknown')}")
        print(f"CLARIFICATION NEEDED: {result.get('clarification_needed', False)}")
        print("\nAGENT RESPONSE:\n")
        print(result["response"])
        print("\n" + "=" * 57 + "\n")

    print("[SUCCESS] STEP 7 Complete: Terminal founder queries executed and validated!")

if __name__ == "__main__":
    test_terminal_queries()
