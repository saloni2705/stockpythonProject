import yfinance as yf
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import datetime
import plotly.graph_objs as go

# Initialize the Dash app
app = dash.Dash()
app.title = "Stock Visualization"

# Layout of the application
app.layout = html.Div(children=[
    html.H1('Stock Visualization Dashboard'),
    html.H4('Enter the stock ticker symbol (e.g., "AAPL" or "TATAMOTORS.NS")'),
    dcc.Input(id="input", value='', type='text', placeholder="Enter stock ticker here"),
    html.Div(id="output-graph"),
])


# Callback for updating the graph
@app.callback(
    Output(component_id="output-graph", component_property='children'),
    [Input(component_id="input", component_property="value")]
)
def update_value(input_data):
    if not input_data:
        return html.Div("Please enter a stock symbol.")

    try:
        start = datetime.datetime(2010, 1, 1)
        end = datetime.datetime.now()

        # Standardize user input
        symbol = input_data.strip().upper()

        # Fetch the stock data using yfinance
        df = yf.download(symbol, start=start, end=end)

        # Debug: Print the dataframe structure and columns to verify 'Close' column
        print(f"Data for {symbol}:\n", df.head())  # Show the first few rows
        print(f"Columns in the dataframe: {df.columns}")

        # Handle the MultiIndex and select the 'Close' column from the correct level
        if 'Close' not in df.columns:
            return html.Div(f"Error: 'Close' column is missing in the data for {symbol}.")

        # Access the 'Close' column using the correct level of the MultiIndex
        df_close = df['Close', symbol]

        # Drop rows with missing 'Close' values
        df_close = df_close.dropna()

        if df_close.empty:
            return html.Div(f"Data for {symbol} contains only missing values.")

        # Explicitly set the range for axes
        x_min, x_max = df_close.index.min(), df_close.index.max()
        y_min, y_max = df_close.min(), df_close.max()

        # Create the line chart
        figure = {
            'data': [go.Scatter(x=df_close.index, y=df_close, mode='lines', name=symbol)],
            'layout': {
                'title': f"Stock Prices for {symbol}",
                'xaxis': {
                    'title': 'Date',
                    'range': [x_min, x_max],
                    'showgrid': True,
                },
                'yaxis': {
                    'title': 'Price (USD)',
                    'range': [y_min * 0.9, y_max * 1.1],  # Add padding to y-axis range
                    'showgrid': True,
                },
            }
        }

        return dcc.Graph(id="demo", figure=figure)

    except Exception as e:
        print(f"Error fetching data for {input_data}: {str(e)}")
        return html.Div(f"Error fetching data for {input_data}: {str(e)}")


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
