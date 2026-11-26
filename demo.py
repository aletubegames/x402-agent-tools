"""Demo: one paid x402 call to Blockchain IQ `brief` ($0.01 USDC on Base).

    X402_PRIVATE_KEY=0x... python demo.py
"""
import json
import os
import sys

from x402client import paid_get

URL = "https://www.blockchainiq.co/api/x402/v1/brief"

key = os.environ.get("X402_PRIVATE_KEY")
if not key:
    sys.exit("set X402_PRIVATE_KEY (hex private key of a wallet holding USDC on Base)")

data, receipt = paid_get(URL, key)
print("data:", json.dumps(data, indent=2)[:1200])
print("settlement tx:", receipt.get("transaction"))
