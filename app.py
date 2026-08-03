from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

API_URL = "https://bcast.jksons.in:7768/VOTSBroadcastStreaming/Services/xml/GetLiveRateByTemplateID/jksons"

last_data = []


def is_number(value):
    try:
        float(value.replace(",", ""))
        return True
    except:
        return False


def fetch_rates():
    global last_data

    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        }

        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()

        lines = response.text.splitlines()

        data = []

        for line in lines:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) < 3:
                continue

            # First column must be item code
            if not parts[0].isdigit():
                continue

            # Last 4 values are prices
            if len(parts) < 6:
                continue

            prices = parts[-4:]

            if not all(is_number(x) for x in prices):
                continue

            name = " ".join(parts[1:-4])

            buy = prices[0]
            sell = prices[1]

            data.append({
                "item_name": name,
                "buy_price": buy,
                "sell_price": sell
            })

        # Auto calculate 22K & 18K
        for item in list(data):

            if "GLD 999 IMP RJT" in item["item_name"]:

                try:

                    rate = float(item["buy_price"].replace(",", ""))

                    c22 = round(rate * 22 / 24, 2)
                    c18 = round(rate * 18 / 24, 2)

                    data.append({
                        "item_name": "GLD 22 CARAT (RJT)",
                        "buy_price": f"{c22:.2f}",
                        "sell_price": f"{c22:.2f}"
                    })

                    data.append({
                        "item_name": "GLD 18 CARAT (RJT)",
                        "buy_price": f"{c18:.2f}",
                        "sell_price": f"{c18:.2f}"
                    })

                except Exception as e:
                    print(e)

        if data:
            last_data = data

    except Exception as e:
        print("Fetch Error:", e)

    return last_data


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/rates")
def rates():
    response = jsonify(fetch_rates())
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
