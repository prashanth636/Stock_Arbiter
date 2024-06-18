import pandas as pd
import numpy as np

def logic_main(volatility, initial_portfolio, stop_loss, take_profit, treasuries):

    # Load the historical data
    data = pd.read_csv('Dropped_ZN_ZB_30m-large.csv', index_col='DateTime')

    # Calculate daily returns
    data['ZN_Return'] = data['ZN'].pct_change()
    data['ZB_Return'] = data['ZB'].pct_change()
    data['return'] = (data['ZN_Return']+data['ZB_Return'])/2

    #data = data[:1000]


    # Calculate rolling volatility for ZN and ZB
    rolling_window = int(volatility)
    print(type(rolling_window))
    data['Rolling_Volatility_ZN'] = data['ZN_Return'].rolling(window=rolling_window).std() * np.sqrt(252)
    data['Rolling_Volatility_ZB'] = data['ZB_Return'].rolling(window=rolling_window).std() * np.sqrt(252)

    # Define thresholds for trade activation for ZB based on ZN volatility
    average_rolling_volatility_ZN = data['Rolling_Volatility_ZN'].rolling(5).mean()
    std_rolling_volatility_ZN = data['Rolling_Volatility_ZN'].rolling(5).std()
    data['volatility_threshold_upper_ZN'] = average_rolling_volatility_ZN + 0.3 * std_rolling_volatility_ZN
    data['volatility_threshold_lower_ZN'] = average_rolling_volatility_ZN - 0.3 * std_rolling_volatility_ZN

    average_rolling_volatility_ZB = data['Rolling_Volatility_ZB'].rolling(5).mean()
    std_rolling_volatility_ZB = data['Rolling_Volatility_ZB'].rolling(5).std()
    data['volatility_threshold_upper_ZB'] = average_rolling_volatility_ZB + 0.3 * std_rolling_volatility_ZB
    data['volatility_threshold_lower_ZB'] = average_rolling_volatility_ZB - 0.3 * std_rolling_volatility_ZB

    print(initial_portfolio)

    initial_portfolio_value = int(initial_portfolio)
    cash_balance = initial_portfolio_value
    open_positions = []
    portfolio_values = {}
    accumulated_pnl_values = []
    closed_positions_pnl_values = []
    trades = 0

    stop_loss_threshold = float(stop_loss)  # 3%
    take_profit_threshold = float(take_profit)  # 5%

    for date_time, row in data.iterrows():
        # Calculate current portfolio value including cash balance and value of open positions
        current_portfolio_value = cash_balance + sum(pos['position'] * row.ZN for pos in open_positions)

        volatility_threshold_upper_ZN = row.volatility_threshold_upper_ZN
        volatility_threshold_lower_ZN = row.volatility_threshold_lower_ZN

        volatility_threshold_upper_ZB = row.volatility_threshold_upper_ZB
        volatility_threshold_lower_ZB = row.volatility_threshold_lower_ZB

        for pos in open_positions:
            val = row.ZN if pos['stock'] == 'ZN' else row.ZB
            if pos['position'] > 0:
                pnl = (val - pos['price']) * pos['position']
                if (pnl < 0 and -(pnl / (pos['price'] * pos['position'])) >= stop_loss_threshold) or (
                        pnl > 0 and (pnl / (pos['price'] * pos['position'])) >= take_profit_threshold):
                    cash_balance += pos['position'] * val
                    closed_positions_pnl_values.append(pnl)
                    trades = trades + 1
                    open_positions.remove(pos)  # Remove closed position
            else:
                x = -pos['position']
                pnl = x * (pos['price'] - val)
                if (pnl < 0 and -(pnl / (pos['price'] * x)) >= stop_loss_threshold) or (
                        pnl > 0 and (pnl / (pos['price'] * x)) >= take_profit_threshold):
                    cash_balance -= x * val
                    # cash_balance += pnl  # Update cash balance
                    closed_positions_pnl_values.append(pnl)  # Store closed position PNL
                    trades = trades + 1
                    open_positions.remove(pos)  # Remove closed position

        # Buy or sell ZB based on adjusted conditions and ZN volatility
        # if row.ZN_Return > 0:
        #     if row.Rolling_Volatility_ZN > volatility_threshold_upper_ZN:
        #         # Sell ZB if return is positive and ZB volatility is negative
        #         ZN_to_sell = 100
        #         cash_balance += ZN_to_sell * row.ZN
        #         open_positions.append({'position': -ZN_to_sell, 'price': row.ZN})
        #     elif row.Rolling_Volatility_ZN < volatility_threshold_lower_ZN :
        #         # Buy ZB if return is positive and ZB volatility is positive
        #         ZN_to_buy = 100
        #         cash_balance -= ZN_to_buy * row.ZN
        #         open_positions.append({'position': ZN_to_buy, 'price': row.ZN})
        # else:
        #     if row.Rolling_Volatility_ZN > volatility_threshold_upper_ZN :
        #         # Buy ZB if return is negative and ZB volatility is negative
        #         ZN_to_buy = 100
        #         cash_balance -= ZN_to_buy * row.ZN
        #         open_positions.append({'position': ZN_to_buy, 'price': row.ZN})
        #     elif row.Rolling_Volatility_ZN < volatility_threshold_lower_ZN :
        #         # Sell ZB if return is negative and ZB volatility is positive
        #         ZN_to_sell = 100
        #         cash_balance += ZN_to_sell * row.ZN
        #         open_positions.append({'position': -ZN_to_sell, 'price': row.ZN})

        if row.ZN_Return > 0:
            if row.Rolling_Volatility_ZN > volatility_threshold_upper_ZN and row.Rolling_Volatility_ZB < volatility_threshold_upper_ZB:
                # Sell ZN and buy ZB if return is positive and ZB volatility is low
                ZN_to_sell = int(treasuries)
                ZB_to_buy = int(treasuries)
                # transaction_cost = transaction_cost_rate * (ZN_to_sell * row.ZN + ZB_to_buy * row.ZB)
                cash_balance += ZN_to_sell * row.ZN - ZB_to_buy * row.ZB
                open_positions.append({'position': -ZN_to_sell, 'price': row.ZN, 'stock': 'ZN'})
                open_positions.append({'position': ZB_to_buy, 'price': row.ZB, 'stock': 'ZB'})
        else:
            if row.Rolling_Volatility_ZN > volatility_threshold_upper_ZN and row.Rolling_Volatility_ZB < volatility_threshold_upper_ZB:
                # Buy ZN and sell ZB if return is negative and ZB volatility is low
                ZN_to_buy = int(treasuries)
                ZB_to_sell = int(treasuries)
                # transaction_cost = transaction_cost_rate * (ZN_to_buy * row.ZN + ZB_to_sell * row.ZB)
                cash_balance += -ZN_to_buy * row.ZN + ZB_to_sell * row.ZB
                open_positions.append({'position': ZN_to_buy, 'price': row.ZN, 'stock': 'ZN'})
                open_positions.append({'position': -ZB_to_sell, 'price': row.ZB, 'stock': 'ZB'})

        if row.ZB_Return > 0:
            if row.Rolling_Volatility_ZN < volatility_threshold_upper_ZN and row.Rolling_Volatility_ZB > volatility_threshold_upper_ZB:
                # Buy ZN and sell ZB if ZB return is positive and ZB volatility is low
                ZN_to_buy = int(treasuries)
                ZB_to_sell = int(treasuries)
                # transaction_cost = transaction_cost_rate * (ZN_to_buy * row.ZN + ZB_to_sell * row.ZB)
                cash_balance += -ZN_to_buy * row.ZN + ZB_to_sell * row.ZB
                open_positions.append({'position': ZN_to_buy, 'price': row.ZN, 'stock': 'ZN'})
                open_positions.append({'position': -ZB_to_sell, 'price': row.ZB, 'stock': 'ZB'})
        else:
            if row.Rolling_Volatility_ZN < volatility_threshold_upper_ZN and row.Rolling_Volatility_ZB > volatility_threshold_upper_ZB:
                # Sell ZN and buy ZB if ZB return is negative and ZB volatility is low
                ZN_to_sell = int(treasuries)
                ZB_to_buy = int(treasuries)
                # transaction_cost = transaction_cost_rate * (ZN_to_sell * row.ZN + ZB_to_buy * row.ZB)
                cash_balance += ZN_to_sell * row.ZN - ZB_to_buy * row.ZB
                open_positions.append({'position': -ZN_to_sell, 'price': row.ZN, 'stock': 'ZN'})
                open_positions.append({'position': ZB_to_buy, 'price': row.ZB, 'stock': 'ZB'})

        # Update portfolio values dictionary with current portfolio value
        portfolio_values[date_time] = cash_balance + sum(pos['position'] * row.ZN for pos in open_positions)
        # Calculate accumulated PNL
        accumulated_pnl = portfolio_values[date_time] - initial_portfolio_value
        accumulated_pnl_values.append(accumulated_pnl)

        if portfolio_values[date_time] <= 0:
            print('portfolio value went to zero on ', date_time)
            break

    # Convert portfolio values to a Series
    portfolio_series = pd.Series(portfolio_values)

    # Convert the index to datetime objects
    portfolio_series.index = pd.to_datetime(portfolio_series.index)

    graph_data_1 = {
        'x': list(portfolio_series.index),
        'y': list(portfolio_series.values),
        'mode': 'lines',
        'name': 'Portfolio Value Over Time (ZB)'
    }

    graph_data_2 = {
        'x': list(data[:len(accumulated_pnl_values)].index),
        'y': accumulated_pnl_values,
        'mode': 'lines',
        'name': 'Accumulated Profit and Loss (P&L) Over Time'
    }

    graph_data_3 = {
        'x': list(data.index[:len(closed_positions_pnl_values)]),
        'y': closed_positions_pnl_values,
        'mode': 'lines',
        'name': 'Closed Positions Profit and Loss (P&L) Over Time'
    }


    graph_data = [graph_data_1, graph_data_2, graph_data_3]

    return {'graph_data': graph_data}