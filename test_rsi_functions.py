import pandas as pd


def is_oversold(rsi_value):
    return rsi_value < 30


def is_overbought(rsi_value):
    return rsi_value > 70


def rsi_status(rsi_value):
    if rsi_value < 30:
        return "OVERSOLD"
    elif rsi_value > 70:
        return "OVERBOUGHT"
    else:
        return "NEUTRAL"


def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# --- Tests for the small helper functions ---
assert is_oversold(24.9) == True
assert is_overbought(84.9) == True
assert rsi_status(50) == "NEUTRAL"

# --- Test for calculate_rsi using synthetic data ---
test_data = {'Close': list(range(100, 120))}
test_df = pd.DataFrame(test_data)

result = calculate_rsi(test_df)
assert result.iloc[-1] > 95

print("All tests passed!")
