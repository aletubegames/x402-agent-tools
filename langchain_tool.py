"""LangChain tool for Blockchain IQ's paid x402 API.

Uses env X402_PRIVATE_KEY by default (or pass private_key=...).
"""
import json
import os
from typing import Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from x402client import paid_get

BRIEF_URL = "https://www.blockchainiq.co/api/x402/v1/brief"
EVENT_RISK_URL = "https://www.blockchainiq.co/api/x402/v1/event-risk"


class _Input(BaseModel):
    resource: str = Field(default="brief",
                          description="'brief' ($0.01) or 'event-risk' ($0.05)")


class BlockchainIQTool(BaseTool):
    name: str = "blockchainiq_x402"
    description: str = (
        "Fetch paid crypto market data from Blockchain IQ. 'brief' returns BTC/ETH/SOL/XRP "
        "prices, 24h/7d/30d moves and next-48h macro events ($0.01 USDC on Base). "
        "'event-risk' returns dated US/crypto risk events 7 days ahead ($0.05). "
        "Paid per-call via x402 — no API key needed.")
    args_schema: Type[BaseModel] = _Input
    private_key: Optional[str] = None

    def _run(self, resource: str = "brief") -> str:
        key = self.private_key or os.environ["X402_PRIVATE_KEY"]
        url = EVENT_RISK_URL if resource == "event-risk" else BRIEF_URL
        data, receipt = paid_get(url, key)
        return json.dumps({"data": data,
                           "settlement_tx": receipt.get("transaction")},
                          ensure_ascii=False)
