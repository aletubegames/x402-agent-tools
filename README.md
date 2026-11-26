# x402 agent tools — Blockchain IQ paid API

LangChain + CrewAI tools that call [Blockchain IQ](https://www.blockchainiq.co)'s
x402 paid endpoints (`brief` $0.01, `event-risk` $0.05) — USDC on Base,
no API keys, payment via EIP-3009 `transferWithAuthorization` settled on-chain.

## Install

```bash
pip install -r requirements.txt
```

## Run the paid demo call

```bash
export X402_PRIVATE_KEY=0x<hex private key with >= $0.01 USDC on Base>
python demo.py
```

Prints the market brief JSON and the settlement transaction hash
(from the `PAYMENT-RESPONSE` header).

## LangChain

```python
from langchain_tool import BlockchainIQTool
tool = BlockchainIQTool()                       # uses X402_PRIVATE_KEY env
print(tool.invoke({"resource": "brief"}))       # {"data": {...}, "settlement_tx": "0x..."}
print(tool.invoke({"resource": "event-risk"}))  # $0.05
```

## CrewAI

```python
from crewai_tool import BlockchainIQCrewTool
tool = BlockchainIQCrewTool()
print(tool._run("brief"))
```

## How it pays

`x402client.paid_get(url, private_key)`:
1. GET → 402 + `PAYMENT-REQUIRED` (base64 JSON with `accepts`)
2. Signs EIP-3009 `transferWithAuthorization` on USDC-Base
   (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`, domain "USD Coin"/"2")
3. Retries with `PAYMENT-SIGNATURE` → facilitator verifies + settles on-chain
4. Returns `(data, receipt)` — receipt has the Base tx hash
