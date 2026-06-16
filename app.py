from flask import Flask, render_template, jsonify
import yfinance as yf
from datetime import datetime

app = Flask(__name__)


def fetch_vix():
    ticker = yf.Ticker("^VIX")
    data = ticker.history(period="1mo")

    if data.empty:
        raise ValueError("No data returned from Yahoo Finance.")

    current = round(float(data['Close'].iloc[-1]), 2)
    prev    = round(float(data['Close'].iloc[-2]), 2)
    change  = round(current - prev, 2)
    pct     = round((change / prev) * 100, 2)
    high_1m = round(float(data['High'].max()), 2)
    low_1m  = round(float(data['Low'].min()), 2)

    chart_labels = [d.strftime('%b %d') for d in data.index]
    closes = [round(float(v), 2) for v in data['Close']]
    highs  = [round(float(v), 2) for v in data['High']]
    lows   = [round(float(v), 2) for v in data['Low']]

    rows = []
    for date, row in data.iloc[::-1].iterrows():
        rows.append({
            'date':  date.strftime('%b %d, %Y'),
            'open':  round(float(row['Open']),  2),
            'high':  round(float(row['High']),  2),
            'low':   round(float(row['Low']),   2),
            'close': round(float(row['Close']), 2),
        })

    if current < 25:
        level, level_class = "Yes", "calm"
    elif current == 25:
        level, level_class = "No", "elevated"
    else:
        level, level_class = "No", "fear"

    return dict(
        current=current, prev=prev, change=change, pct=pct,
        high_1m=high_1m, low_1m=low_1m, level=level, level_class=level_class,
        chart_labels=chart_labels, closes=closes, highs=highs, lows=lows,
        rows=rows,
        updated=datetime.utcnow().strftime('%b %d, %Y at %H:%M UTC'),
        error=None
    )


def fetch_spus():
    ticker = yf.Ticker("SPUS")
    data = ticker.history(period="1mo")

    if data.empty:
        raise ValueError("No data returned from Yahoo Finance.")

    current = round(float(data['Close'].iloc[-1]), 2)
    prev    = round(float(data['Close'].iloc[-2]), 2)
    change  = round(current - prev, 2)
    pct     = round((change / prev) * 100, 2)
    high_1m = round(float(data['High'].max()), 2)
    low_1m  = round(float(data['Low'].min()), 2)

    chart_labels = [d.strftime('%b %d') for d in data.index]
    closes = [round(float(v), 2) for v in data['Close']]
    highs  = [round(float(v), 2) for v in data['High']]
    lows   = [round(float(v), 2) for v in data['Low']]

    # Analysis: Open - Low, only on days where Open < Close (bullish days)
    analysis_rows = []
    for date, row in data.iloc[::-1].iterrows():
        o = round(float(row['Open']),  2)
        h = round(float(row['High']),  2)
        l = round(float(row['Low']),   2)
        c = round(float(row['Close']), 2)
        bullish = o < c
        open_minus_low = round(o - l, 2) if bullish else None
        analysis_rows.append({
            'date':          date.strftime('%b %d, %Y'),
            'open':          o,
            'high':          h,
            'low':           l,
            'close':         c,
            'bullish':       bullish,
            'open_minus_low': open_minus_low,
        })

    # Average of Open - Low for bullish days only
    values = [r['open_minus_low'] for r in analysis_rows if r['open_minus_low'] is not None]
    avg_open_minus_low = round(sum(values) / len(values), 2) if values else 0
    bullish_count = len(values)

    return dict(
        current=current, prev=prev, change=change, pct=pct,
        high_1m=high_1m, low_1m=low_1m,
        chart_labels=chart_labels, closes=closes, highs=highs, lows=lows,
        analysis_rows=analysis_rows,
        avg_open_minus_low=avg_open_minus_low,
        bullish_count=bullish_count,
        total_days=len(analysis_rows),
        updated=datetime.utcnow().strftime('%b %d, %Y at %H:%M UTC'),
        error=None
    )


@app.route('/')
def index():
    try:
        ctx = fetch_vix()
    except Exception as e:
        ctx = dict(error=str(e))
    return render_template('index.html', **ctx)


@app.route('/spus')
def spus():
    try:
        ctx = fetch_spus()
    except Exception as e:
        ctx = dict(error=str(e))
    return render_template('spus.html', **ctx)


@app.route('/api/vix')
def api_vix():
    try:
        ctx = fetch_vix()
        return jsonify(ctx)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
