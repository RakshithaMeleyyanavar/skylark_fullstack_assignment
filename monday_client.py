"""
Monday.com Live GraphQL API Client.

IMPORTANT SECURITY & DESIGN CONSTRAINTS:
1. READ-ONLY ACCESS: Performs ONLY GraphQL `query` operations. NEVER uses GraphQL `mutation`.
2. LIVE API FETCH: All data is fetched live from Monday.com API. No CSV/Excel files stored on disk.
3. IN-MEMORY TTL CACHE: Used for performance optimization only (2-5 min TTL). Source of truth is live API.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from cache import TTLCache

load_dotenv()

MONDAY_API_URL = "https://api.monday.com/v2"

# 3-minute in-memory TTL cache for live API calls
_cache = TTLCache(ttl_seconds=180)

class MondayClient:
    """Client for fetching live board data from Monday.com GraphQL API."""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("MONDAY_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "MONDAY_API_TOKEN environment variable is missing. "
                "Please set it in your .env file or environment."
            )

    def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a READ-ONLY GraphQL query against Monday.com API.
        Guaranteed read-only: query strings contain ONLY 'query' keyword, never 'mutation'.
        """
        if "mutation" in query.lower():
            raise SecurityError("READ-ONLY VIOLATION: Mutations are strictly prohibited!")

        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(MONDAY_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        res_data = response.json()

        if "errors" in res_data:
            raise RuntimeError(f"Monday API Error: {res_data['errors']}")

        return res_data.get("data", {})

    def fetch_board_items_raw(self, board_id: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch all raw items from a given board using items_page cursor pagination.
        Includes optional in-memory TTL caching for performance.
        """
        cache_key = f"raw_board_{board_id}"
        if use_cache:
            cached_data = _cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        query = """
        query GetBoardItems($board_id: [ID!], $cursor: String) {
          boards(ids: $board_id) {
            id
            name
            items_page(limit: 100, cursor: $cursor) {
              cursor
              items {
                id
                name
                column_values {
                  id
                  type
                  text
                  value
                }
              }
            }
          }
        }
        """

        all_items: List[Dict[str, Any]] = []
        cursor: Optional[str] = None

        while True:
            variables: Dict[str, Any] = {"board_id": [str(board_id)]}
            if cursor:
                variables["cursor"] = cursor

            data = self._execute_query(query, variables)
            boards = data.get("boards", [])
            if not boards:
                break

            items_page = boards[0].get("items_page", {})
            items = items_page.get("items", [])
            all_items.extend(items)

            cursor = items_page.get("cursor")
            if not cursor or not items:
                break

        if use_cache:
            _cache.set(cache_key, all_items)

        return all_items

    @staticmethod
    def parse_item_columns(item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw item object into a flat record dictionary.
        - Item title (Deal Name / Deal name masked) is stored under key 'name'.
        - Column values use column_id as key.
        - Handles status/dropdown nested JSON vs text values per schema requirements.
        """
        record: Dict[str, Any] = {
            "item_id": item.get("id"),
            "name": item.get("name", "").strip()
        }

        for col in item.get("column_values", []):
            col_id = col.get("id")
            col_type = col.get("type", "")
            raw_text = col.get("text")
            raw_val = col.get("value")

            parsed_value = None

            # Handle status / dropdown vs standard types
            if raw_val:
                try:
                    val_json = json.loads(raw_val)
                    if isinstance(val_json, dict):
                        # Status columns usually have 'label' or 'text' inside JSON
                        if "label" in val_json:
                            parsed_value = val_json["label"]
                        elif "text" in val_json:
                            parsed_value = val_json["text"]
                        elif "labels" in val_json and isinstance(val_json["labels"], list):
                            parsed_value = ", ".join(val_json["labels"])
                except (json.JSONDecodeError, TypeError):
                    pass

            # Fallback to display text if nested parse did not return a value
            if parsed_value is None:
                parsed_value = raw_text if raw_text is not None else ""

            # Standardize empty strings to None/empty string consistently
            if isinstance(parsed_value, str):
                parsed_value = parsed_value.strip()

            record[col_id] = parsed_value

        return record

    def fetch_board_data(self, board_id: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Fetch and parse all items for a given board into flat dictionary records."""
        raw_items = self.fetch_board_items_raw(board_id, use_cache=use_cache)
        return [self.parse_item_columns(item) for item in raw_items]


class SecurityError(Exception):
    """Raised when a mutation operation is attempted on read-only client."""
    pass
