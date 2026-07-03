from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from dotenv import set_key

from app.config import ROOT, Settings
from app.database import Database
from app.schemas import AnalysisContext, WatchedToken
from app.services.ai_agent_service import AIAgentService
from app.services.market_data_service import MarketDataService
from app.services.openai_service import OpenAIService
from app.services.paper_trading_service import PaperTradingService
from app.services.risk_service import RiskService
from app.services.solana_service import SolanaService
from app.services.token_metadata_service import TokenMetadataService
from app.services.trade_proposal_service import TradeProposalService
from app.services.wallet_service import WalletService
from app.utils.constants import SOL_MINT
from app.utils.formatters import percent, usd
from app.utils.validators import validate_solana_address


st.set_page_config(
    page_title="Phantom AI DEX Portal",
    page_icon="SOL",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; color: #f8fafc; }
.stApp {
    background-color: #070b14;
    background-image:
        radial-gradient(ellipse 70% 45% at 10% 0%, rgba(20,184,166,.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 55% at 95% 20%, rgba(99,102,241,.09) 0%, transparent 58%);
}
#MainMenu, footer { visibility: hidden; }
.portal-title {
    font-size: 2.25rem; font-weight: 800; letter-spacing: 0;
    background: linear-gradient(135deg, #5eead4 0%, #818cf8 55%, #f59e0b 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 4px 0;
}
.portal-subtitle { color: #94a3b8; margin: 0 0 20px 0; font-size: .95rem; }
.glass-card {
    background: rgba(15,23,42,.72);
    border: 1px solid rgba(148,163,184,.16);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 16px 36px rgba(0,0,0,.24);
}
.metric-card {
    background: rgba(15,23,42,.74);
    border: 1px solid rgba(148,163,184,.15);
    border-radius: 12px;
    padding: 18px 18px 16px;
    min-height: 112px;
}
.metric-label { color: #94a3b8; font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; }
.metric-value { color: #f8fafc; font-size: 1.72rem; line-height: 1.2; font-weight: 800; margin-top: 8px; }
.status-pill { display:inline-flex; padding:5px 12px; border-radius:999px; font-size:.78rem; font-weight:700; }
.status-green { color:#34d399; background:rgba(16,185,129,.11); border:1px solid rgba(16,185,129,.28); }
.status-yellow { color:#fbbf24; background:rgba(245,158,11,.11); border:1px solid rgba(245,158,11,.28); }
.status-red { color:#f87171; background:rgba(239,68,68,.11); border:1px solid rgba(239,68,68,.28); }
div.stButton > button:first-child {
    background: linear-gradient(135deg, #0f766e 0%, #4f46e5 100%);
    color: white; border: none; border-radius: 10px; font-weight: 700;
}
div.stButton > button:first-child:hover {
    background: linear-gradient(135deg, #14b8a6 0%, #6366f1 100%);
    color: white; border: none;
}
[data-testid="stSidebar"] { background: rgba(8,13,24,.95); }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def services() -> dict[str, Any]:
    settings = Settings()
    database = Database(settings.database_path)
    metadata = TokenMetadataService()
    risk = RiskService(database, risk_config(database, settings))
    return {
        "settings": settings,
        "db": database,
        "wallet": WalletService(SolanaService(settings.solana_rpc_url)),
        "market": MarketDataService(metadata, settings.birdeye_api_key),
        "risk": risk,
        "proposals": TradeProposalService(database, risk),
        "paper": PaperTradingService(database, settings.dry_run),
    }


def refresh_services() -> dict[str, Any]:
    services.clear()
    return services()


def query_db(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return services()["db"].query(sql, params)


def execute_db(sql: str, params: tuple[Any, ...] = ()) -> int:
    return services()["db"].execute(sql, params)


def setting(key: str, default: str = "") -> str:
    rows = query_db("SELECT value FROM settings WHERE key=?", (key,))
    return rows[0]["value"] if rows else default


def set_setting(key: str, value: str) -> None:
    execute_db(
        "INSERT INTO settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


def risk_config(database: Database, settings: Settings) -> dict[str, Any]:
    config = settings.risk_dict()
    rows = database.query("SELECT key,value FROM settings WHERE key LIKE 'risk.%'")
    for row in rows:
        name = row["key"].removeprefix("risk.")
        if name not in config:
            continue
        if isinstance(config[name], bool):
            config[name] = row["value"].lower() == "true"
        elif isinstance(config[name], int):
            config[name] = int(float(row["value"]))
        else:
            config[name] = float(row["value"])
    return config


def latest_wallet() -> dict[str, Any]:
    rows = query_db("SELECT payload FROM wallet_snapshots ORDER BY id DESC LIMIT 1")
    if rows:
        return json.loads(rows[0]["payload"])
    return {
        "public_address": setting("wallet_address"),
        "total_value_usd": 0,
        "sol_balance": 0,
        "tokens": [],
    }


def watched_tokens() -> list[dict[str, Any]]:
    return query_db("SELECT * FROM watched_tokens ORDER BY symbol")


def metric(label: str, value: str, tone: str = "") -> None:
    color = "#f8fafc"
    if tone == "green":
        color = "#34d399"
    elif tone == "yellow":
        color = "#fbbf24"
    elif tone == "red":
        color = "#f87171"
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value" style="color:{color};">{value}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def safe_json_loads(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


def proposal_rows() -> list[dict[str, Any]]:
    rows = query_db("SELECT * FROM trade_proposals ORDER BY id DESC")
    items = []
    for row in rows:
        payload = safe_json_loads(row["payload"])
        trade = payload.get("suggested_trade") or {}
        items.append(
            {
                "id": row["id"],
                "decision": row["decision"],
                "confidence": payload.get("confidence"),
                "amount_usd": trade.get("amount_usd", 0),
                "risk_score": row["risk_score"],
                "status": row["status"],
                "created_at": row["created_at"],
                "payload": payload,
            }
        )
    return items


def decision_color(decision: str) -> str:
    return {
        "BUY": "green",
        "DCA": "green",
        "SELL": "yellow",
        "TAKE_PROFIT": "yellow",
        "HOLD": "",
        "AVOID": "red",
    }.get(decision, "")


def valid_ai_key(api_key: str) -> bool:
    clean = (api_key or "").strip()
    if not clean:
        return False
    if clean.upper().startswith("OPENAI_API_KEY") or clean.lower() in {"your_key_here", "sk-..."}:
        return False
    return clean.startswith("sk-") or clean.startswith("nvapi-")


def render_header() -> None:
    settings = services()["settings"]
    st.markdown('<h1 class="portal-title">Phantom AI DEX Portal</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="portal-subtitle">Solana wallet intelligence, AI risk decisions, manual proposals, dry-run execution.</p>',
        unsafe_allow_html=True,
    )
    mode = "DRY RUN" if settings.dry_run else "REVIEW ONLY"
    pill = "status-green" if settings.dry_run else "status-yellow"
    st.markdown(
        f'<span class="status-pill {pill}">{mode}</span> '
        '<span class="status-pill status-yellow">Manual approval required</span> '
        '<span class="status-pill status-red">No private keys</span>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    settings = services()["settings"]
    with st.sidebar:
        st.markdown("## Phantom AI")
        st.caption("DEX Assistant")
        st.divider()
        wallet = latest_wallet()
        st.metric("Wallet Value", usd(wallet.get("total_value_usd")))
        st.metric("SOL Balance", f"{float(wallet.get('sol_balance') or 0):,.4f}")
        st.caption(f"Model: `{settings.openai_model}`")
        st.caption(f"Database: `{settings.database_path.name}`")
        st.divider()
        st.info("Research and paper trading only. No seed phrase, no private key, no automatic live swap.")


def dashboard_tab() -> None:
    svc = services()
    wallet = latest_wallet()
    stats = svc["paper"].performance()
    tokens = wallet.get("tokens", [])
    watched = watched_tokens()

    cols = st.columns(4)
    with cols[0]:
        metric("Wallet Value", usd(wallet.get("total_value_usd")))
    with cols[1]:
        metric("SOL Balance", f"{float(wallet.get('sol_balance') or 0):,.4f}")
    with cols[2]:
        metric("Paper Trades", str(stats.get("trades") or 0))
    with cols[3]:
        pnl = float(stats.get("pnl") or 0)
        metric("Paper PnL", usd(pnl), "green" if pnl >= 0 else "red")

    left, right = st.columns([3, 2])
    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Wallet Coins & Watchlist")
        rows = [
            {
                "symbol": "SOL",
                "name": "Solana",
                "balance": float(wallet.get("sol_balance") or 0),
                "value_usd": None,
                "exposure": None,
                "risk": "LOW",
                "source": "Wallet",
                "mint": SOL_MINT,
            }
        ]
        watched_by_mint = {row["mint_address"]: row for row in watched}
        holding_mints = set()
        for token in tokens:
            mint = token.get("mint")
            holding_mints.add(mint)
            meta = watched_by_mint.get(mint, {})
            rows.append(
                {
                    "symbol": meta.get("symbol", "UNKNOWN"),
                    "name": meta.get("name", "Wallet token"),
                    "balance": token.get("amount"),
                    "value_usd": token.get("value_usd"),
                    "exposure": token.get("exposure_percent"),
                    "risk": meta.get("risk_level", "HIGH"),
                    "source": "Wallet",
                    "mint": mint,
                }
            )
        for mint, token in watched_by_mint.items():
            if mint not in holding_mints:
                rows.append(
                    {
                        "symbol": token["symbol"],
                        "name": token["name"],
                        "balance": 0,
                        "value_usd": None,
                        "exposure": 0,
                        "risk": token["risk_level"],
                        "source": "Watchlist",
                        "mint": mint,
                    }
                )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Safety State")
        risk = risk_config(svc["db"], svc["settings"])
        st.write(f"Max trade size: **{risk['max_trade_percent_of_wallet']}%**")
        st.write(f"Max token exposure: **{risk['max_exposure_per_token_percent']}%**")
        st.write(f"Min liquidity: **{usd(risk['minimum_liquidity_usd'])}**")
        st.write(f"Max daily trades: **{risk['max_trades_per_day']}**")
        st.write(f"Max price impact: **{risk['max_price_impact_percent']}%**")
        st.markdown("</div>", unsafe_allow_html=True)


def wallet_tab() -> None:
    svc = services()
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Public Wallet Snapshot")
    current = setting("wallet_address")
    address = st.text_input("Phantom public wallet address", value=current, placeholder="Paste public Solana address")
    if st.button("Refresh Wallet Snapshot", use_container_width=True):
        try:
            clean = validate_solana_address(address)
            set_setting("wallet_address", clean)
            with st.spinner("Reading Solana wallet balances..."):
                snapshot = svc["wallet"].snapshot(clean)
                svc["db"].save_snapshot(snapshot.model_dump(mode="json"))
            st.success("Snapshot saved.")
            st.rerun()
        except Exception as error:
            st.error(str(error))
    st.markdown("</div>", unsafe_allow_html=True)

    wallet = latest_wallet()
    st.dataframe(pd.DataFrame(wallet.get("tokens", [])), use_container_width=True, hide_index=True)


def market_tab() -> None:
    svc = services()
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Solana DEX Market")
    search, col_btn, col_active = st.columns([5, 1, 1])
    query = search.text_input("Search symbol, name, pair, or mint", value="", label_visibility="collapsed")
    search_clicked = col_btn.button("Search", use_container_width=True)
    active_clicked = col_active.button("Active", use_container_width=True)
    st.caption("Discovery data is not an endorsement. Verify mint, liquidity, and metadata before adding anything.")

    if "dex_rows" not in st.session_state:
        st.session_state.dex_rows = []

    try:
        if search_clicked and query.strip():
            with st.spinner("Searching DexScreener..."):
                st.session_state.dex_rows = svc["market"].search_solana_dex(query.strip())
        elif active_clicked or not st.session_state.dex_rows:
            with st.spinner("Loading active Solana DEX market..."):
                st.session_state.dex_rows = svc["market"].fetch_solana_dex_market(100)
    except Exception as error:
        st.warning(f"Market data unavailable: {error}")

    rows = st.session_state.dex_rows
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Add Market Token To Watchlist")
    options = [f"{row.get('symbol')} | {row.get('mint')}" for row in rows if row.get("mint")]
    choice = st.selectbox(
        "Market token",
        options,
        index=0 if options else None,
        placeholder="Load market data first",
        key="market_token_select",
    )
    allowed = st.checkbox("Allowed for proposals", value=False)
    if st.button("Add Selected Token", use_container_width=True, disabled=not choice):
        mint = choice.split(" | ", 1)[1]
        coin = next((row for row in rows if row.get("mint") == mint), {})
        existing = query_db("SELECT symbol FROM watched_tokens WHERE mint_address=?", (mint,))
        if existing:
            st.info(f"{existing[0]['symbol']} is already in the watchlist.")
        else:
            token = WatchedToken(
                mint_address=mint,
                symbol=coin.get("symbol") or "UNKNOWN",
                name=coin.get("name") or "Unknown token",
                category="dex-discovery",
                notes="Added from Streamlit DEX discovery; verify mint and metadata.",
                allowed_for_trading=allowed,
            )
            data = token.model_dump(mode="json")
            keys = [
                "mint_address",
                "symbol",
                "name",
                "category",
                "notes",
                "allowed_for_trading",
                "blocked",
                "risk_level",
                "reason_for_blocking",
                "created_at",
                "updated_at",
            ]
            execute_db("INSERT INTO watched_tokens VALUES(?,?,?,?,?,?,?,?,?,?,?)", tuple(data[key] for key in keys))
            st.success(f"{token.symbol} added to watchlist.")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def watchlist_tab() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Watched Tokens")
    tokens = watched_tokens()
    st.dataframe(pd.DataFrame(tokens), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([2, 1])
    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Add / Update Token")
        with st.form("watch_token_form"):
            mint = st.text_input("Mint address")
            symbol = st.text_input("Symbol", value="UNKNOWN")
            name = st.text_input("Name", value="Unknown token")
            category = st.text_input("Category", value="uncategorized")
            notes = st.text_area("Notes")
            risk_level = st.selectbox(
                "Risk level",
                ["LOW", "MEDIUM", "HIGH", "EXTREME"],
                index=2,
                key="watchlist_risk_level_select",
            )
            allowed = st.checkbox("Allowed for proposals", value=True)
            blocked = st.checkbox("Blocked", value=False)
            submitted = st.form_submit_button("Save Token", use_container_width=True)
        if submitted:
            try:
                clean = validate_solana_address(mint)
                token = WatchedToken(
                    mint_address=clean,
                    symbol=symbol.strip() or "UNKNOWN",
                    name=name.strip() or "Unknown token",
                    category=category.strip() or "uncategorized",
                    notes=notes.strip(),
                    risk_level=risk_level,
                    allowed_for_trading=allowed,
                    blocked=blocked,
                )
                data = token.model_dump(mode="json")
                keys = [
                    "mint_address",
                    "symbol",
                    "name",
                    "category",
                    "notes",
                    "allowed_for_trading",
                    "blocked",
                    "risk_level",
                    "reason_for_blocking",
                    "created_at",
                    "updated_at",
                ]
                execute_db("INSERT OR REPLACE INTO watched_tokens VALUES(?,?,?,?,?,?,?,?,?,?,?)", tuple(data[key] for key in keys))
                st.success("Token saved.")
                st.rerun()
            except Exception as error:
                st.error(str(error))
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Remove Token")
        options = [f"{row['symbol']} | {row['mint_address']}" for row in tokens]
        remove_choice = st.selectbox(
            "Token",
            options,
            index=0 if options else None,
            placeholder="No tokens",
            key="remove_watchlist_token_select",
        )
        confirm = st.checkbox("Confirm removal")
        if st.button("Remove Selected", use_container_width=True, disabled=not remove_choice or not confirm):
            mint = remove_choice.split(" | ", 1)[1]
            execute_db("DELETE FROM watched_tokens WHERE mint_address=?", (mint,))
            st.success("Token removed.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def analysis_tab() -> None:
    svc = services()
    tokens = watched_tokens()
    options = [f"{row['symbol']} | {row['mint_address']}" for row in tokens]
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Token Market Analysis")
    choice = st.selectbox(
        "Watched token",
        options,
        index=0 if options else None,
        placeholder="Add a token first",
        key="analysis_watched_token_select",
    )
    if st.button("Fetch Market Data", use_container_width=True, disabled=not choice):
        mint = choice.split(" | ", 1)[1]
        try:
            with st.spinner("Fetching token metadata and DEX liquidity..."):
                st.session_state.market_analysis = svc["market"].fetch(mint)
        except Exception as error:
            st.error(str(error))
    data = st.session_state.get("market_analysis")
    if data:
        st.json(data)
    st.markdown("</div>", unsafe_allow_html=True)


def ai_agent_tab() -> None:
    svc = services()
    settings = svc["settings"]
    tokens = watched_tokens()
    options = [f"{row['symbol']} | {row['mint_address']}" for row in tokens]
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("AI Trade Decision Engine")
    choice = st.selectbox(
        "Watched token",
        options,
        index=0 if options else None,
        placeholder="Add a token first",
        key="ai_watched_token_select",
    )
    create_button = st.button("Generate Structured AI Decision", use_container_width=True, disabled=not choice)
    if create_button:
        if not valid_ai_key(settings.openai_api_key):
            st.warning(
                "AI key is missing or still looks like a placeholder. Open Settings and add a real sk-... OpenAI key "
                "or nvapi-... NVIDIA key, then save."
            )
        else:
            mint = choice.split(" | ", 1)[1]
            token = next((row for row in tokens if row["mint_address"] == mint), None)
            try:
                with st.spinner("Fetching market data and asking the AI risk assistant..."):
                    market = svc["market"].fetch(mint)
                    wallet = latest_wallet()
                    context = AnalysisContext(
                        wallet=wallet,
                        watchlist=tokens,
                        market_data=[market],
                        risk_settings=risk_config(svc["db"], settings),
                        trading_rules={
                            "manual_approval_required": True,
                            "never_all_in": True,
                            "partial_profit_taking": True,
                        },
                        previous_trades=query_db("SELECT * FROM dry_run_trades ORDER BY id DESC LIMIT 20"),
                        open_positions=query_db("SELECT * FROM paper_portfolio"),
                    )
                    openai = OpenAIService(settings.openai_api_key, settings.openai_model, settings.openai_base_url)
                    decision = AIAgentService(openai, svc["db"]).analyze(context)
                    proposal_id = svc["proposals"].create(decision, market, token or {}, wallet)
                    st.session_state.last_ai_result = {
                        "decision": decision.model_dump(mode="json"),
                        "proposal_id": proposal_id,
                        "market": market,
                    }
            except Exception as error:
                st.error(str(error))

    result = st.session_state.get("last_ai_result")
    if result:
        decision = result["decision"]
        cols = st.columns(4)
        with cols[0]:
            metric("Decision", decision.get("decision", "-"), decision_color(decision.get("decision", "")))
        with cols[1]:
            metric("Confidence", f"{decision.get('confidence', 0)}%")
        with cols[2]:
            metric("Risk", decision.get("risk_level", "-"), "red" if decision.get("risk_level") in {"HIGH", "EXTREME"} else "yellow")
        with cols[3]:
            proposal_id = result.get("proposal_id")
            metric("Proposal", f"#{proposal_id}" if proposal_id else "Blocked", "green" if proposal_id else "red")
        st.markdown("#### Reasoning")
        st.write(decision.get("reasoning_summary"))
        left, right = st.columns(2)
        with left:
            st.markdown("#### Suggested Trade")
            st.json(decision.get("suggested_trade") or {})
        with right:
            st.markdown("#### Risk Plan")
            st.json(
                {
                    "entry_zones": decision.get("entry_zones"),
                    "dca_zones": decision.get("dca_zones"),
                    "take_profit_zones": decision.get("take_profit_zones"),
                    "stop_loss_zone": decision.get("stop_loss_zone"),
                    "invalid_trade_conditions": decision.get("invalid_trade_conditions"),
                    "warnings": decision.get("warnings"),
                }
            )
    st.markdown("</div>", unsafe_allow_html=True)


def proposals_tab() -> None:
    svc = services()
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Trade Proposals")
    rows = proposal_rows()
    display = [{k: v for k, v in row.items() if k != "payload"} for row in rows]
    st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Manual Review")
    options = [f"#{row['id']} | {row['decision']} | {row['status']}" for row in rows]
    choice = st.selectbox(
        "Proposal",
        options,
        index=0 if options else None,
        placeholder="No proposals",
        key="proposal_review_select",
    )
    action = st.radio("Action", ["Approve", "Reject", "Execute Paper Trade"], horizontal=True)
    reject_reason = st.text_input("Reject reason", value="Rejected from web portal", disabled=action != "Reject")
    confirm = st.checkbox("I understand this is a manual DRY_RUN workflow")
    if st.button("Apply Action", use_container_width=True, disabled=not choice or not confirm):
        proposal_id = int(choice.split(" | ", 1)[0].removeprefix("#"))
        try:
            if action == "Approve":
                svc["proposals"].set_status(proposal_id, True)
                st.success(f"Proposal #{proposal_id} approved.")
            elif action == "Reject":
                svc["proposals"].set_status(proposal_id, False, reject_reason)
                st.success(f"Proposal #{proposal_id} rejected.")
            else:
                result = svc["paper"].execute_approved(proposal_id)
                st.success("Paper trade executed.")
                st.json(result)
            st.rerun()
        except Exception as error:
            st.error(str(error))
    st.markdown("</div>", unsafe_allow_html=True)


def portfolio_tab() -> None:
    svc = services()
    stats = svc["paper"].performance()
    cols = st.columns(5)
    values = [
        ("Trades", str(stats.get("trades") or 0), ""),
        ("Wins", str(stats.get("wins") or 0), "green"),
        ("Losses", str(stats.get("losses") or 0), "red"),
        ("Rejected", str(stats.get("rejected") or 0), "yellow"),
        ("PnL", usd(stats.get("pnl")), "green" if float(stats.get("pnl") or 0) >= 0 else "red"),
    ]
    for col, (label, value, tone) in zip(cols, values):
        with col:
            metric(label, value, tone)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Paper Positions")
    st.dataframe(pd.DataFrame(query_db("SELECT * FROM paper_portfolio")), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Dry-run Trade History")
    st.dataframe(pd.DataFrame(query_db("SELECT * FROM dry_run_trades ORDER BY id DESC")), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


def settings_tab() -> None:
    svc = services()
    settings = svc["settings"]
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("AI Provider")
    with st.form("ai_settings_form"):
        api_key = st.text_input("API key", value=settings.openai_api_key, type="password")
        model = st.text_input("Model", value=settings.openai_model)
        base_url = st.text_input("Base URL", value=settings.openai_base_url)
        save_ai = st.form_submit_button("Save AI Settings", use_container_width=True)
    if save_ai:
        if not api_key.strip():
            st.error("API key is required for AI analysis.")
        else:
            if api_key.startswith("nvapi-") and not base_url.strip():
                base_url = "https://integrate.api.nvidia.com/v1"
            env_path = ROOT / ".env"
            env_path.touch(exist_ok=True)
            set_key(str(env_path), "OPENAI_API_KEY", api_key.strip(), quote_mode="never")
            set_key(str(env_path), "OPENAI_MODEL", model.strip() or "gpt-4.1-mini", quote_mode="never")
            set_key(str(env_path), "OPENAI_BASE_URL", base_url.strip(), quote_mode="never")
            os.environ["OPENAI_API_KEY"] = api_key.strip()
            os.environ["OPENAI_MODEL"] = model.strip() or "gpt-4.1-mini"
            os.environ["OPENAI_BASE_URL"] = base_url.strip()
            refresh_services()
            st.success("AI settings saved locally.")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Risk Limits")
    current = risk_config(svc["db"], settings)
    with st.form("risk_settings_form"):
        fields: dict[str, Any] = {}
        for key, value in current.items():
            disabled = key in {"dry_run", "manual_approval_required"}
            fields[key] = st.text_input(key.replace("_", " ").title(), value=str(value), disabled=disabled)
        save_risk = st.form_submit_button("Save Risk Settings", use_container_width=True)
    if save_risk:
        try:
            for key, value in fields.items():
                if key in {"dry_run", "manual_approval_required"}:
                    continue
                float(value)
                set_setting(f"risk.{key}", value)
            refresh_services()
            st.success("Risk settings saved.")
            st.rerun()
        except ValueError:
            st.error("All editable risk values must be numeric.")
    st.markdown("</div>", unsafe_allow_html=True)


def logs_tab() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Recent Logs")
    path = Path(ROOT) / "data" / "app.log"
    lines = path.read_text(encoding="utf-8").splitlines()[-220:] if path.exists() else []
    st.code("\n".join(lines) or "No log entries yet.", language="text")
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    render_sidebar()
    render_header()
    tabs = st.tabs(
        [
            "Performance",
            "Wallet",
            "DEX Market",
            "Watchlist",
            "Analysis",
            "AI Agent",
            "Proposals",
            "Portfolio",
            "Settings",
            "Logs",
        ]
    )
    with tabs[0]:
        dashboard_tab()
    with tabs[1]:
        wallet_tab()
    with tabs[2]:
        market_tab()
    with tabs[3]:
        watchlist_tab()
    with tabs[4]:
        analysis_tab()
    with tabs[5]:
        ai_agent_tab()
    with tabs[6]:
        proposals_tab()
    with tabs[7]:
        portfolio_tab()
    with tabs[8]:
        settings_tab()
    with tabs[9]:
        logs_tab()


if __name__ == "__main__":
    main()
