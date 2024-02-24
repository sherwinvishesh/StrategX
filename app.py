from flask import Flask, request, render_template_string
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>StrategX</title>
    <link rel="stylesheet" href="/static/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
    <h2>Enter Stock Information</h2>
    <form method="post">
        <label for="ticker">Ticker Symbol:</label><br>
        <input type="text" id="ticker" name="ticker" required><br>
        <label for="start">Start Date:</label><br>
        <input type="date" id="start" name="start_date" required><br>
        <label for="end">End Date:</label><br>
        <input type="date" id="end" name="end_date" required><br><br>
        <input type="submit" value="Submit">
    </form>
    <footer>Made with ❤️ by Sherwin</footer>
</body>
</html>
'''

def fetch_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Calculate G-Channel
def calculate_g_channel(data, length=5):
    a = pd.Series(0.0, index=data.index)
    b = pd.Series(0.0, index=data.index)
    for i in range(1, len(data)):
        a.iloc[i] = max(data['Close'].iloc[i], a.iloc[i-1]) - (a.iloc[i-1] - b.iloc[i-1]) / length
        b.iloc[i] = min(data['Close'].iloc[i], b.iloc[i-1]) + (a.iloc[i-1] - b.iloc[i-1]) / length
    data['G_Channel_A'] = a
    data['G_Channel_B'] = b
    return data

# Calculate EMA
def calculate_ema(data, length=200):
    data['EMA'] = data['Close'].ewm(span=length, adjust=False).mean()
    return data

# Calculate EMA ribbon
def calculate_ema_ribbon(data, lengths):
    for length in lengths:
        data[f'EMA_{length}'] = data['Close'].ewm(span=length, adjust=False).mean()
    return data

# Calculate KNN 
def calculate_knn(data, N=10, K=100):
    # Ensure data has enough points
    if len(data) < N + 1:
        return data
    
    data['KNN_Pred'] = np.nan
    for i in range(N, len(data)):
        segment = data['Close'].iloc[i-N:i].values
        current_close = data['Close'].iloc[i]
        
        # Calculate distances and sort them
        distances = np.abs(segment[:-1] - current_close)
        sorted_indices = np.argsort(distances)
        
        # Select K nearest neighbors and calculate the average
        if K > len(sorted_indices):
            K = len(sorted_indices)
        nearest_neighbors = segment[sorted_indices[:K]]
        prediction = np.mean(nearest_neighbors)
        
        # Store the prediction
        data['KNN_Pred'].iloc[i] = prediction
    
    return data


# Calculate ATR
def calculate_atr(data, length=14):
    data['High-Low'] = data['High'] - data['Low']
    data['High-PrevClose'] = abs(data['High'] - data['Close'].shift(1))
    data['Low-PrevClose'] = abs(data['Low'] - data['Close'].shift(1))
    tr = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    data['ATR'] = tr.rolling(window=length).mean()
    return data

# Calculate buy and sell signals
def calculate_indicators(data, atr_multiplier_sl=2, atr_multiplier_tp=4):
    crossup = (data['G_Channel_B'].shift() < data['Close'].shift()) & (data['G_Channel_B'] > data['Close'])
    crossdn = (data['G_Channel_A'].shift() > data['Close'].shift()) & (data['G_Channel_A'] < data['Close'])
    data['Buy_Signal'] = crossup & (data['Close'] < data['EMA'])
    data['Sell_Signal'] = crossdn & (data['Close'] > data['EMA'])

    data['Long_SL'] = data['Close'] - atr_multiplier_sl * data['ATR']
    data['Long_TP'] = data['Close'] + atr_multiplier_tp * data['ATR']
    return data

def plot_strategy(data, ticker):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(data['Close'], label='Close Price', color='skyblue')
    ax.plot(data['G_Channel_A'], label='G-Channel Upper', color='red', linestyle='--')
    ax.plot(data['G_Channel_B'], label='G-Channel Lower', color='green', linestyle='--')
    ax.plot(data['EMA'], label='EMA', color='orange', linewidth=2)
    ax.scatter(data.index[data['Buy_Signal']], data['Close'][data['Buy_Signal']], label='Buy', marker='^', color='green', alpha=1)
    ax.scatter(data.index[data['Sell_Signal']], data['Close'][data['Sell_Signal']], label='Sell', marker='v', color='red', alpha=1)
    # Plot EMA Ribbon
    ema_lengths = [8, 14, 20, 26, 32, 38, 44, 50, 60]
    data = calculate_ema_ribbon(data, ema_lengths)
    for length in ema_lengths:
        ema_label = f'EMA_{length}'
        ax.plot(data.index, data[ema_label], label=ema_label, linewidth=1)

    data = calculate_knn(data, N=10, K=100)  # You can adjust N and K as needed
    ax.plot(data.index, data['KNN_Pred'], label='KNN Prediction', color='magenta', linewidth=2)
        

    # Continue with existing plotting code...
    ax.set_title(f'{ticker} ')
    ax.legend(loc='upper left')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return image_base64

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Check if the start date is before the end date
        if pd.to_datetime(start_date) >= pd.to_datetime(end_date):
            return "Error: The start date must be before the end date. Please go back and enter a valid date range."


        data = fetch_stock_data(ticker, start_date, end_date)
        if data.empty:
            return "Error: No data available for the given date range. Please try a different range."
        
        data = calculate_g_channel(data)
        data = calculate_ema(data)
        data = calculate_atr(data)
        data = calculate_indicators(data)
        
        image = plot_strategy(data, ticker)
        return f'<img src="data:image/png;base64,{image}"><br><footer>Made with ❤️ by Sherwin</footer>'
    else:
        return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(debug=True)
