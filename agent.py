"""
Conversational BI Agent with Google Gemini Tool Calling.

Manages prompt context, system prompt with schema & data caveats,
Google Gemini tool-calling loop, response synthesis, and clarifying-question logic.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

import google.generativeai as genai
from tools import get_deals, get_work_orders, get_cross_board_view, get_data_quality_report

load_dotenv()

SYSTEM_PROMPT = """
You are a Senior Executive Conversational BI Agent connected LIVE and READ-ONLY to Monday.com boards.

DATA DICTIONARY & SCHEMA MAP:
1. Board 1: Deal Funnel Data (board_id: 5030221175, ~346 raw rows, 344 valid rows after excluding 2 corrupt rows)
   - Deal Name (item title)
   - Owner code (OWNER_001-008)
   - Client Code (COMPANY0xx, 199 distinct)
   - Deal Status (Won/Dead/Open/On Hold; Note: 2 corrupted header-literal rows excluded)
   - Masked Deal value (numeric, 52% null - ALWAYS disclose null % when aggregating deal values)
   - Tentative Close Date (use for quarterly queries)
   - Sector/service (12 values, non-sector junk like Tender/DSP filtered)

2. Board 2: Work_Order_Tracker Data (board_id: 5030221237, ~176 rows)
   - Deal name masked (different pool, ~15.4% exact overlap with Board 1)
   - Customer Name Code (WOCOMPANY_XXX, separate namespace from Client Code, NOT joinable)
   - BD/KAM Personnel code (SAME namespace as Board 1 Owner code - SAFE JOIN KEY)
   - Sector (SAME label set as Board 1 Sector - SAFE JOIN KEY)
   - Execution Status (Completed/Ongoing/Not Started/Pause-struck)
   - Amount Receivable (Masked, CAN BE NEGATIVE credit - NEVER clip to zero)
   - Expected Billing Month / Actual Collection Month / Collection Status / Collection Date (100% null - treat as 'not tracked')

JOIN RULES:
- SAFE JOINS: Owner code <-> BD/KAM Personnel code; Sector <-> Sector.
- BEST-EFFORT JOIN: Deal Name <-> Deal name masked exact match (~15.4% coverage).
- NEVER claim deal-level financial reconciliation unless name match succeeded.

DATA QUALITY MANDATE:
- Never silently hide missing data - detect & disclose nulls, corrupt rows, and join gaps in every answer.
- Ask a clarifying question on genuine ambiguity (e.g. unmatched sector name) instead of guessing.
"""

class BIAgent:
    """Conversational BI Agent managing tool calls and response synthesis."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.use_simulated = (not self.api_key or "your_gemini_api_key" in self.api_key or self.api_key == "mock-key")

        if not self.use_simulated:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=SYSTEM_PROMPT,
                    tools=[get_deals, get_work_orders, get_cross_board_view, get_data_quality_report]
                )
            except Exception as e:
                print(f"[WARN] Failed to initialize Gemini model: {e}")
                self.use_simulated = True

    def run_query(self, user_query: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Execute user query through Gemini tool calling loop or deterministic tool router."""
        if not self.use_simulated:
            try:
                chat = self.model.start_chat(enable_automatic_function_calling=True)
                response = chat.send_message(user_query)
                res_text = response.text if hasattr(response, 'text') else str(response)

                clarifying = "?" in res_text and any(phrase in res_text.lower() for phrase in ["did you mean", "could you clarify", "please specify"])

                return {
                    "response": res_text,
                    "clarification_needed": clarifying,
                    "engine": "Google Gemini 1.5 Flash (Live Function Calling)"
                }
            except Exception as e:
                print(f"[FALLBACK] Gemini API call exception: {e}")

        # Deterministic tool router fallback (works offline or when API key is pending)
        return self._deterministic_tool_router(user_query)

    def _deterministic_tool_router(self, query: str) -> Dict[str, Any]:
        """Deterministic tool dispatcher for terminal testing and key fallback."""
        q_lower = query.lower()

        if "quality" in q_lower or "health" in q_lower or "completeness" in q_lower or "null" in q_lower:
            report = get_data_quality_report("all")
            deals_warn = report["deal_funnel_board"]["high_null_warnings"]
            wo_untracked = report["work_order_board"]["untracked_fields"]
            res = (
                f"### Data Health & Completeness Audit Report\n\n"
                f"**Board 1 (Deal Funnel)**: Total 344 valid rows (2 corrupt header-literal rows excluded).\n"
                f"**High Null Warnings**: {', '.join(deals_warn)}\n\n"
                f"**Board 2 (Work Order Tracker)**: Total 176 rows.\n"
                f"**Untracked Fields (100% Null)**: {', '.join(wo_untracked)}\n\n"
                f"*(Disclosed per data quality mandate)*"
            )
            return {"response": res, "clarification_needed": False, "engine": "Deterministic Data Quality Engine"}

        elif "cross" in q_lower or "owner" in q_lower or "personnel" in q_lower or "sector" in q_lower:
            cross_data = get_cross_board_view()
            summary = cross_data["summary_table"][:5]
            caveat = cross_data["join_rule_caveat"]
            res = (
                f"### Cross-Board Aggregate Analysis (Safe Join on Owner Code)\n\n"
                f"Showing top 5 Owner aggregate groups:\n\n"
                f"```json\n{json.dumps(summary, indent=2)}\n```\n\n"
                f"**Data Caveat & Join Rule**:\n{caveat}"
            )
            return {"response": res, "clarification_needed": False, "engine": "Deterministic Cross-Board Engine"}

        elif "deal" in q_lower or "funnel" in q_lower or "won" in q_lower or "open" in q_lower:
            status_filter = "Won" if "won" in q_lower else ("Open" if "open" in q_lower else None)
            deals_data = get_deals(status=status_filter)
            res = (
                f"### Deal Funnel Summary ({deals_data['total_deals_found']} deals found)\n\n"
                f"- **Total Reported Masked Deal Value**: ${deals_data['sum_masked_value']:,.2f}\n"
                f"- **Data Quality Caveat**: {deals_data['data_caveat']}\n"
                f"- **Excluded Corrupt Rows**: {deals_data['excluded_corrupt_rows']}\n"
            )
            return {"response": res, "clarification_needed": False, "engine": "Deterministic Deals Engine"}

        elif "work order" in q_lower or "receivable" in q_lower or "collection" in q_lower or "billed" in q_lower:
            wo_data = get_work_orders()
            res = (
                f"### Work Order Financial Summary ({wo_data['total_work_orders_found']} work orders)\n\n"
                f"- **Total Billed (excl GST)**: ${wo_data['total_billed_excl_gst']:,.2f}\n"
                f"- **Total Collected (incl GST)**: ${wo_data['total_collected_incl_gst']:,.2f}\n"
                f"- **Total Amount Receivable**: ${wo_data['total_amount_receivable']:,.2f} *(includes credit balances)*\n"
                f"- **Data Quality Caveat**: {wo_data['data_caveat']}\n"
            )
            return {"response": res, "clarification_needed": False, "engine": "Deterministic Work Order Engine"}

        else:
            res = (
                "Could you please clarify your question? For example:\n"
                "1. *'What is our total deal value for Won deals?'*\n"
                "2. *'Show me cross-board performance by Owner code.'*\n"
                "3. *'What is the data quality and completeness report for both boards?'*"
            )
            return {"response": res, "clarification_needed": True, "engine": "Clarification Engine"}
