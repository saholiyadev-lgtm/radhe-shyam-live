from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# સર્વર ચાલુ થાય ત્યારે ક્યારેય ખાલી ના દેખાય એ માટે ડિફોલ્ટ લાઈવ ડેટા
last_valid_data = [
    {"item_name": "GOLD", "buy_price": "4065.65", "sell_price": "4065.65"},
    {"item_name": "SILVER", "buy_price": "58.18", "sell_price": "58.18"},
    {"item_name": "USD INR", "buy_price": "95.390", "sell_price": "95.390"},
    {"item_name": "GLD 999 IMP AMD T+1", "buy_price": "147260", "sell_price": "147260"},
    {"item_name": "GLD 999 IMP RJT T+1", "buy_price": "147280", "sell_price": "147280"},
    {"item_name": "GLD 22 CARAT (RJT)", "buy_price": "135006.67", "sell_price": "135006.67"},
    {"item_name": "GLD 18 CARAT (RJT)", "buy_price": "110460.00", "sell_price": "110460.00"},
    {"item_name": "SLVCHORSA T+1", "buy_price": "220580", "sell_price": "220580"},
    {"item_name": "SLVPETI999 T+1", "buy_price": "224500", "sell_price": "224500"},
    {"item_name": "SLV 999 (1 KG BAR) T+1", "buy_price": "226500", "sell_price": "226500"}
]

def fetch_live_jk_rates():
    global last_valid_data
    
    timestamp = int(time.time() * 1000)
    url = f"https://jksons.in/?_={timestamp}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://jksons.in/',
        'Cache-Control': 'no-cache'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            live_data = []
            
            # જ્વેલરી રેટ ટેબલ સ્ક્રેપિંગ
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        product = cells[0].text.strip()
                        rate = cells[1].text.strip()
                        
                        if product and rate and "SYMBOL" not in product.upper() and "RATE" not in rate.upper():
                            live_data.append({
                                "item_name": product,
                                "buy_price": rate,
                                "sell_price": rate
                            })
                            
                            # ૨૨ અને ૧૮ કેરેટની કેલ્ક્યુલેશન
                            if "GLD 999" in product.upper() and "RJT" in product.upper():
                                try:
                                    clean_rate = float(rate.replace(',', ''))
                                    
                                    c22 = round((clean_rate * 22) / 24, 2)
                                    live_data.append({
                                        "item_name": "GLD 22 CARAT (RJT)",
                                        "buy_price": f"{c22:,.2f}",
                                        "sell_price": f"{c22:,.2f}"
                                    })
                                    
                                    c18 = round((clean_rate * 18) / 24, 2)
                                    live_data.append({
                                        "item_name": "GLD 18 CARAT (RJT)",
                                        "buy_price": f"{c18:,.2f}",
                                        "sell_price": f"{c18:,.2f}"
                                    })
                                except ValueError:
                                    pass

            if len(live_data) > 0:
                last_valid_data = live_data

    except Exception as e:
        print(f"Error scraping: {e}")
        
    return last_valid_data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rates')
def get_rates():
    rates = fetch_live_jk_rates()
    response = jsonify(rates)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
