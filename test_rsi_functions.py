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


def calculate_vwap(df):
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    tp_volume = typical_price * df['Volume']
    cumulative_tp_volume = tp_volume.cumsum()
    cumulative_volume = df['Volume'].cumsum()
    return cumulative_tp_volume / cumulative_volume


def calculate_bollinger_bands(df, period=20):
    middle = df['Close'].rolling(period).mean()
    std = df['Close'].rolling(period).std()
    upper = middle + (2 * std)
    lower = middle - (2 * std)
    return middle, upper, lower


def get_hod_lod(df):
    hod = df['High'].iloc[-1]
    lod = df['Low'].iloc[-1]
    return hod, lod


# --- Tests for the small helper functions ---
assert is_oversold(24.9) == True
assert is_overbought(84.9) == True
assert rsi_status(50) == "NEUTRAL"

# --- Test for calculate_rsi using synthetic data ---
test_data_rsi = {'Close': list(range(100, 120))}
test_df_rsi = pd.DataFrame(test_data_rsi)
result_rsi = calculate_rsi(test_df_rsi)
assert result_rsi.iloc[-1] > 95

# --- Test for calculate_vwap using synthetic data ---
test_data_vwap = {
    'High': [100, 100, 100, 100, 100],
    'Low': [100, 100, 100, 100, 100],
    'Close': [100, 100, 100, 100, 100],
    'Volume': [1000, 2000, 1500, 3000, 500]
}
test_df_vwap = pd.DataFrame(test_data_vwap)
result_vwap = calculate_vwap(test_df_vwap)
assert result_vwap.iloc[-1] == 100


# --- Test for calculate_bollinger_bands using constant prices ---
def test_bollinger_bands_constant_prices():
    test_df = pd.DataFrame({'Close': [100.0] * 25})
    middle, upper, lower = calculate_bollinger_bands(test_df, period=20)
    assert middle.iloc[-1] == 100.0
    assert upper.iloc[-1] == middle.iloc[-1]
    assert lower.iloc[-1] == middle.iloc[-1]


test_bollinger_bands_constant_prices()

# --- Test for get_hod_lod ---
test_df_hodlod = pd.DataFrame({
    'High': [100.5, 102.0, 105.0],
    'Low': [98.0, 99.5, 101.5]
})
hod, lod = get_hod_lod(test_df_hodlod)
assert hod == 105.0
assert lod == 101.5

print("All tests passed!")
