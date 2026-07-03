# Crypto Trading Simulator

Projekt edukativ ne Python me version desktop dhe web app ne Streamlit.

## Cfare ka brenda

- Market prices per Bitcoin, Ethereum, Solana dhe Cardano
- Demo prices pa internet
- Opsion `Use CoinGecko API` nese ka internet
- Buy/Sell simulator
- Portfolio tracker me cash, holdings dhe total value
- Watchlist
- Trade history
- AI Market Assistant me trend, risk dhe sugjerim
- Grafik i cmimit ne desktop dhe ne web app
- Ruajtje manuale ne `portfolio.json`

## Si hapet web app

Nga ky folder:

```powershell
cd "Kursi Python\Dita10\CryptoTradingSimulator"
python -m pip install -r requirements.txt
python run_web_app.py
```

Pastaj hape linkun qe shfaqet ne terminal, zakonisht:

```text
http://localhost:8501
```

Mund ta nisesh edhe direkt me Streamlit:

```powershell
python -m streamlit run streamlit_app.py
```

## Si hapet desktop app

Nga folderi kryesor i projektit:

```powershell
python "Kursi Python\Dita10\CryptoTradingSimulator\crypto_trading_simulator.py"
```

## Si perdoret

1. Kliko `Refresh` per te krijuar levizje te reja ne market.
2. Zgjidh nje coin nga tabela ose nga dropdown.
3. Te `USD / coin amount`, shkruaj:
   - USD per `Buy USD`
   - sasi coin per `Sell Coin`
4. Kliko `Save` per te ruajtur portofolin.
5. Perdor `Add Watch` dhe `Remove` per watchlist.

Ky projekt eshte simulator per mesim, jo keshille financiare.
