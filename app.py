# app.py
from flask import Flask, request, jsonify, render_template
import arbitrage_backtest as backend

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get form data
    #stocks = request.form.get('stocks')
    volatility = request.form.get('volatility')
    initial_portfolio = request.form.get('initial-portfolio')
    #transaction_cost = request.form.get('transaction_cost')
    stop_loss = request.form.get('stop-loss')
    take_profit = request.form.get('take-profit')
    treasuries = request.form.get('treasuries')
    #mean_volatility = request.form.get('mean_volatility')

    # Call your Python backend function
    result = backend.logic_main(volatility, initial_portfolio, stop_loss, take_profit, treasuries)

    # Prepare data for the frontend
    # graph_data = {
    #   'data': result['graph_data'],
    #   'layout': {
    #       'title': 'Stock Returns',
    #       'xaxis': {'title': 'Date'},
    #       'yaxis': {'title': 'Returns'}
    #   }
    # }
    # metrics = result['metrics']

    graph_data = result.get('graph_data', [])  # Get graph_data from result, or an empty list if not found
    metrics = result.get('metrics', {})  # Get metrics from result, or an empty dictionary if not found

    return jsonify({'graph_data': graph_data, 'metrics': metrics})

if __name__ == '__main__':
  app.run(debug=True)