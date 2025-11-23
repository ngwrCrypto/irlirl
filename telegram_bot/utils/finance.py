import httpx

async def get_exchange_rates() -> str:
    try:
        async with httpx.AsyncClient() as client:
            # 1. Fiat (NBU API for UAH)
            # https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json
            fiat_url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
            fiat_resp = await client.get(fiat_url)
            fiat_data = fiat_resp.json()

            usd_uah = next((item['rate'] for item in fiat_data if item['cc'] == 'USD'), 0.0)
            eur_uah = next((item['rate'] for item in fiat_data if item['cc'] == 'EUR'), 0.0)

            # 2. Crypto (CoinGecko API)
            # https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd
            crypto_url = "https://api.coingecko.com/api/v3/simple/price"
            crypto_params = {
                "ids": "bitcoin,ethereum",
                "vs_currencies": "usd"
            }
            crypto_resp = await client.get(crypto_url, params=crypto_params)
            crypto_data = crypto_resp.json()

            btc_usd = crypto_data.get('bitcoin', {}).get('usd', 0.0)
            eth_usd = crypto_data.get('ethereum', {}).get('usd', 0.0)

            return (
                f"💰 Курс валют:\n"
                f"🇺🇸 USD: {usd_uah:.2f} ₴\n"
                f"🇪🇺 EUR: {eur_uah:.2f} ₴\n\n"
                f"💎 Крипта:\n"
                f"₿ BTC: {btc_usd:,.2f} $\n"
                f"Ξ ETH: {eth_usd:,.2f} $"
            )

    except Exception as e:
        return f"Помилка отримання курсів: {e}"
