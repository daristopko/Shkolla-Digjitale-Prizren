# Python Phantom AI DEX Agent

A conservative, Python-only desktop and terminal assistant for inspecting a public Solana wallet, maintaining a token watchlist, checking DEX market conditions, asking OpenAI for structured trade decisions, and simulating manually approved proposals.

It is an analysis and paper-trading tool, not a profit bot. It never asks for or stores a seed phrase or private key, never signs transactions, and never submits an automatic live trade.

## Safety model

- `DRY_RUN=true` is the default.
- Only a public wallet address is needed to read balances.
- AI output is validated as structured JSON with Pydantic.
- Actionable decisions pass through deterministic risk checks.
- Every accepted proposal starts as `PENDING` and needs explicit terminal approval.
- Approved proposals can only become `EXECUTED_DRY_RUN` in this version.
- Jupiter swap preparation is review/export only. Final execution requires a trusted Phantom-compatible signing flow and visible wallet approval.

The Python-only application cannot safely bypass Phantom's wallet approval model. Private-key or backend signing is deliberately absent.

## Features

- Dashboard and public-wallet snapshots via Solana RPC
- SPL token balances, estimated values, and exposure when prices are available
- SQLite-backed watchlist with allow/block and risk metadata
- Jupiter quote adapter and DexScreener-compatible market adapter
- Token metadata and suspicious-name checks
- BUY, SELL, HOLD, DCA, TAKE_PROFIT, and AVOID AI decisions
- Risk limits for size, concentration, loss, frequency, slippage, impact, metadata, and liquidity
- Manual proposal approval/rejection and paper-trade history
- Local logs and editable risk settings

Market data can be incomplete or delayed. Unknown price, liquidity, metadata, or route information should be treated as risk, not reassurance.

## Install

Python 3.11 or newer is required.

```powershell
cd Dita11\python-phantom-ai-dex-agent
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill `OPENAI_API_KEY` in `.env`. Keep `DRY_RUN=true`. Other limits can be changed in `.env` or through the Risk Settings screen. Never put a seed phrase or wallet private key in `.env`.

## Run

```powershell
python main.py
```

This launches the Tkinter desktop interface. The original Rich terminal interface remains available with:

```powershell
python main.py --terminal
```

The Streamlit web portal is available with:

```powershell
streamlit run web_app.py
```

It provides the same safety-first workflow in a browser: wallet snapshots, DEX discovery, watchlist management, token analysis, AI decisions, manual proposal review, dry-run execution, risk settings, and logs.

1. Open **Wallet** and enter a Phantom public address. The snapshot is stored locally in `data/app.db`.
2. Open **Watchlist**, choose `add`, and enter the exact token mint. Verify symbol and name carefully.
3. Open **Token Analysis** to inspect current metadata, price, and liquidity.
4. Open **AI Agent**, select a watched mint, and request a structured decision.
5. Review any resulting proposal under **Proposals**. Approval is manual and defaults to no.
6. After approval, confirm paper execution. No blockchain transaction is sent.

If `OPENAI_API_KEY` is absent, wallet, watchlist, market, history, and risk features still work; AI analysis shows a clear configuration error.

## Data and tables

SQLite initializes `settings`, `watched_tokens`, `wallet_snapshots`, `ai_analyses`, `trade_proposals`, `dry_run_trades`, `executed_trades`, `rejected_trades`, `risk_events`, and `paper_portfolio`. Raw and parsed AI responses are retained for auditing. Logs are written to `data/app.log`.

## Real swap preparation

`JupiterService.prepare_swap_export()` packages quote details with a signing warning. It does not create a signature or send a transaction. A future integration may export serialized transaction data to a trusted Phantom-compatible signing surface, but wallet confirmation must remain explicit.

## Disclaimer

Crypto assets and DEX routes are highly risky. AI output can be wrong, manipulated, or based on stale data. This software provides research assistance only and is not financial advice. Validate token mints, liquidity, fees, price impact, and wallet prompts independently.

## Future improvements

- Historical candles and richer liquidity adapters
- Token-program and mint-authority analysis
- Cost-basis imports and mark-to-market paper PnL
- Scheduled scans with APScheduler, disabled by default
- Explicit transaction export for reviewed Phantom-compatible signing
- Automated tests with mocked RPC, DEX, and OpenAI responses
