# StrategX

StrategX is a web-based application designed to provide comprehensive stock analysis and predictions. Utilizing historical stock data, the application offers technical analysis, trend predictions, and visualization tools to help users make informed investment decisions.

## Features

- **Stock Data Fetching**: Leverages `yfinance` to fetch historical stock data.
- **Technical Analysis**: Includes G-Channel, EMA, EMA Ribbon, KNN Predictions, and ATR indicators.
- **Stock Prediction**: Uses ARIMA model for forecasting future stock prices.
- **Visualization**: Generates interactive time-series graphs and technical analysis charts.
- **Downloadable Forecast Data**: Allows users to download forecast data as CSV files.
- User-friendly web interface for inputting stock ticker and date range.
- Professional styling with CSS and integration of the Lato font for better user experience.

## User Interface


https://github.com/sherwinvishesh/StrategX/assets/60791187/b624ba17-8ffd-4d17-9de0-156b3aebbb3a




## Installation

To run StrategX on your local machine, you need Python 3.6+ installed. Follow these steps:

1. Clone this repository to your local machine.
    ```bash
    git clone https://github.com/sherwinvishesh/StrategX.git
    ```
2. Navigate to the project directory.
    ```bash
    cd StrategX
    ```
3. Install the required Python packages.
    ```bash
    pip3 install pandas numpy matplotlib yfinance flask base64 plotly 
    ```
    `If you are getting any errors while installing the above`
    Then you have to create a virtual environment and run this program, here are the steps:
    Create a Virtual Environment:
    ```bash
    python3 -m venv path/to/venv
    ```
    Activate the Virtual Environment:
    mac or linux 
    ```bash
    source path/to/venv/bin/activate
    ```

    For Windows:
    ```bash
    path\to\venv\Scripts\activate
    ```

4. Run the Flask application.
    ```bash
    python3 app.py
    ```





# Usage

After running the application, access it at `http://127.0.0.1:5000/`:

1. Enter the ticker symbol for the stock you're interested in.
2. Select a start date for historical data analysis.
3. Click on "Submit" to view the stock data, technical analysis charts, and predictions.

## Indicators Used

- **G-Channel**: A custom indicator that uses the maximum and minimum of close prices over a specified period to plot upper and lower bounds. It's useful for identifying potential breakout points.
- **EMA (Exponential Moving Average)**: A type of moving average that places a greater weight and significance on the most recent data points. It's commonly used to identify the trend direction.
- **ATR SL/TP (Average True Range Stop Loss/Take Profit)**: Utilizes the ATR indicator to determine optimal stop loss and take profit levels based on market volatility.
- **KNN (K-Nearest Neighbors) Based Indicator**: A machine learning approach used here to predict future stock prices based on the analysis of historical price data. It identifies patterns by looking at the 'K' most similar instances (neighbors) and averaging their values for the prediction.

## Technologies

- **Flask**: A lightweight WSGI web application framework in Python, used for building web applications quickly and with minimal setup.
- **yfinance**: A Python library that allows for easy access to financial data available on Yahoo Finance, including historical market data and metadata.
- **Pandas**: An open-source data analysis and manipulation tool in Python, providing data structures and operations for manipulating numerical tables and time series.
- **NumPy**: A fundamental package for scientific computing in Python, offering support for large, multi-dimensional arrays and matrices, along with a collection of mathematical functions to operate on these arrays.
- **Matplotlib**: A plotting library for the Python programming language and its numerical mathematics extension NumPy, used for creating static, interactive, and animated visualizations in Python.
- **Plotly**: An interactive, open-source plotting library that supports over 40 unique chart types covering a wide range of statistical, financial, geographic, scientific, and 3-dimensional use-cases.
- **ARIMA from statsmodels**: Explained below.

## About Stock Prediction

StrategX utilizes the AutoRegressive Integrated Moving Average (ARIMA) model for predicting future stock prices. ARIMA is a popular statistical analysis model that captures various standard temporal structures in time series data.

### How ARIMA Works

ARIMA models are characterized by three primary parameters: (p, d, q):
- `p` is the order of the autoregressive part,
- `d` is the degree of differencing (the number of times the data have had past values subtracted),
- `q` is the order of the moving average part.

In essence, ARIMA models aim to describe the autocorrelations in the time series data. For the stock prediction feature in StrategX, we specifically use:

- Historical closing prices of the stock as input.
- A predefined model order (for example, (5,1,0)) which was empirically found to perform well for a general range of stocks. This includes 5 past terms for the AR part, 1 difference to make the time series stationary, and no moving average component.
- The model is then trained on the historical data, and future stock prices are forecasted over a specified horizon.

### Implementation in StrategX

Here's a simplified overview of how ARIMA is implemented in StrategX for stock prediction:

1. **Data Preparation**: The historical stock data fetched using `yfinance` is preprocessed, focusing on the closing prices. The data is split based on the selected start date by the user, providing a series of daily closing prices.

2. **Model Fitting**: The ARIMA model is fitted to the prepared dataset. In StrategX, we have predefined the ARIMA model parameters, but users can modify these parameters for experimental purposes.

3. **Prediction**: Once the model is fitted, it forecasts future stock prices over the desired prediction horizon. This horizon is set by the application but can be adjusted for longer or shorter forecasts.

4. **Visualization and Download**: The forecasted stock prices are then visualized alongside historical data using Plotly for an interactive experience. Additionally, users have the option to download the forecast data as a CSV file for further analysis.

### Why ARIMA?

ARIMA was chosen for its simplicity and effectiveness in handling a wide range of time series data, making it suitable for stock price predictions. It offers a balance between model complexity and predictive power, providing users with a straightforward yet powerful tool for financial analysis.

While ARIMA is capable of producing reasonably accurate forecasts, users should be aware of the inherent volatility and unpredictability of the stock market. Predictions are based on historical data patterns and do not account for unforeseen market movements or external factors.

For those interested in exploring more advanced or alternative prediction models, StrategX's modular design allows for easy integration and experimentation with different statistical or machine learning approaches.



## Contributing

Contributions to enhance this project are welcomed. Please feel free to fork the repository, make changes, and submit pull requests.

## Support

If you encounter any issues or have any questions, please submit an issue on the GitHub issue tracker or feel free to contact me.


## License

StrategX is open source and available under the [MIT License](LICENSE).

## Acknowledgments


- Thanks to everyone who visits and uses this page. Your interest and feedback are what keep us motivated.
- Special thanks to all the contributors who help maintain and improve this project. Your dedication and hard work are greatly appreciated.
## Connect with Me

Feel free to reach out and connect with me on [LinkedIn](https://www.linkedin.com/in/sherwinvishesh) or [Instagram](https://www.instagram.com/sherwinvishesh/).

---

Made with ❤️ by Sherwin
