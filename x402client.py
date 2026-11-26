"""Minimal x402 v2 client — EIP-3009 (transferWithAuthorization) signing for EVM networks.

Usage:
    from x402client import paid_get
    data, receipt = paid_get(url, private_key)
"""
import base64
import json
import secrets
import time

import httpx
from eth_account import Account
from eth_account.messages import encode_typed_data


def _sign_eip3009(acct: Account, req: dict) -> dict:
    chain_id = int(req["network"].split(":")[1])
    nonce = "0x" + secrets.token_hex(32)
    va = str(int(time.time()) - 600)
    vb = str(int(time.time()) + req.get("maxTimeoutSeconds", 300))
    auth = {"from": acct.address, "to": req["payTo"], "value": req["amount"],
            "validAfter": va, "validBefore": vb, "nonce": nonce}
    typed = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"}],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"}],
        },
        "primaryType": "TransferWithAuthorization",
        "domain": {"name": req["extra"]["name"], "version": req["extra"]["version"],
                   "chainId": chain_id, "verifyingContract": req["asset"]},
        "message": {**auth, "value": int(auth["value"]),
                    "validAfter": int(va), "validBefore": int(vb)},
    }
    sig = acct.sign_message(encode_typed_data(full_message=typed)).signature.hex()
    return {"x402Version": 2,
            "payload": {"authorization": auth, "signature": "0x" + sig},
            "accepted": req}


def _decode_challenge(headers, body):
    raw = headers.get("PAYMENT-REQUIRED")
    if raw:
        return json.loads(base64.b64decode(raw))
    return body


def paid_get(url: str, private_key: str, network: str = "eip155:8453",
             timeout: int = 60) -> tuple[dict, dict]:
    """GET `url` paying x402 on `network`. Returns (json_body, settle_receipt)."""
    acct = Account.from_key(private_key)
    r = httpx.get(url, timeout=timeout)
    if r.status_code != 402:
        raise RuntimeError(f"expected 402, got {r.status_code}: {r.text[:300]}")
    challenge = _decode_challenge(r.headers, r.json())
    req = next((a for a in challenge["accepts"] if a["network"] == network), None)
    if not req:
        raise RuntimeError(f"network {network} not accepted: "
                           f"{[a['network'] for a in challenge['accepts']]}")
    sig_b64 = base64.b64encode(
        json.dumps(_sign_eip3009(acct, req)).encode()).decode()
    r2 = httpx.get(url, timeout=timeout, headers={"PAYMENT-SIGNATURE": sig_b64})
    if r2.status_code != 200:
        raise RuntimeError(f"paid call failed {r2.status_code}: {r2.text[:300]}")
    receipt = {}
    raw = r2.headers.get("PAYMENT-RESPONSE")
    if raw:
        receipt = json.loads(base64.b64decode(raw))
    return r2.json(), receipt
