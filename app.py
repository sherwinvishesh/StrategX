from flask import Flask, request, render_template, Response
import yfinance as yf
import pandas as pd
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objs as go
from plotly.io import to_html
import numpy as np  # Ensure this is included


app = Flask(__name__)
app.config['PROJECT_NAME'] = 'StrategX'
forecast_csv = None  # Global variable to hold the forecast CSV data

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
    global forecast_csv  # Declare global to modify the global variable

    if request.method == 'POST':
        ticker = request.form['ticker']
        # start_date = request.form['start_date']
        end_date = date.today().strftime('%Y-%m-%d')

        # if pd.to_datetime(start_date) >= pd.to_datetime(end_date):
        #     return "Error: Start date must be before the end date."

        ticker_obj = yf.Ticker(ticker)
        history = ticker_obj.history(period="max")  # Fetches the maximum history
        if history.empty:
            return "Error: No data available for this ticker."
        
        start_date = history.index[0].strftime('%Y-%m-%d') 

        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            return "Error: No data available for the given date range."

        # Technical analysis and plot
        data = calculate_g_channel(data)
        data = calculate_ema(data)
        data = calculate_ema_ribbon(data, [8, 14, 20, 26, 32, 38, 44, 50, 60])
        data = calculate_knn(data)
        data = calculate_atr(data)
        data = calculate_indicators(data)
        image_base64 = plot_strategy(data, ticker)

        # Time series data plot
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=data.index, y=data["Open"], name="Stock Open"))
        fig1.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Stock Close"))
        fig1.layout.update(title_text="Time Series Data", xaxis_rangeslider_visible=True)
        graph_html_1 = to_html(fig1, full_html=False)

        # Forecasting
        df_train = data[['Close']]
        model = ARIMA(df_train, order=(5,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=7)  # Forecasting for the next week

        future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=7, freq='D')
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=future_dates, y=forecast, name='Forecast'))
        fig2.layout.update(title_text="Forecast Data", xaxis_title="Date", yaxis_title="Price")
        graph_html_2 = to_html(fig2, full_html=False)

        forecast_csv = forecast.to_csv()  # Store the forecast CSV data for download

        return render_template("index.html", graph_html_1=graph_html_1, graph_html_2=graph_html_2, image_base64=image_base64)
    else:
        return render_template("index.html", graph_html_1=None, graph_html_2=None, image_base64=None)


@app.route('/download_forecast')
def download_forecast():
    if forecast_csv is None:
        return "No forecast data available to download."

    return Response(
        forecast_csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=forecast.csv"})

if __name__ == '__main__':
    app.run(debug=True)
