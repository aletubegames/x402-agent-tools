"""CrewAI tool for Blockchain IQ's paid x402 API."""
import json
import os
from typing import Optional, Type

from pydantic import BaseModel, Field

from x402client import paid_get

try:
    from crewai.tools import BaseTool
except ImportError:  # crewai not installed — keep importable for docs/tests
    class BaseTool:  # type: ignore
        pass

BRIEF_URL = "https://www.blockchainiq.co/api/x402/v1/brief"
EVENT_RISK_URL = "https://www.blockchainiq.co/api/x402/v1/event-risk"


class _Input(BaseModel):
    resource: str = Field(default="brief",
                          description="'brief' ($0.01) or 'event-risk' ($0.05)")


class BlockchainIQCrewTool(BaseTool):
    name: str = "blockchainiq_x402"
    description: str = (
        "Paid crypto market brief/event-risk from Blockchain IQ via x402 "
        "(USDC on Base, no API key). 'brief' = prices + 48h events ($0.01); "
        "'event-risk' = 7-day risk calendar ($0.05).")
    args_schema: Type[BaseModel] = _Input
    private_key: Optional[str] = None

    def _run(self, resource: str = "brief") -> str:
        key = self.private_key or os.environ["X402_PRIVATE_KEY"]
        url = EVENT_RISK_URL if resource == "event-risk" else BRIEF_URL
        data, receipt = paid_get(url, key)
        return json.dumps({"data": data,
                           "settlement_tx": receipt.get("transaction")},
                          ensure_ascii=False)
