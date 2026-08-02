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

assert is_oversold(24.9) == True
assert is_overbought(84.9) == True
assert rsi_status(50) == "NEUTRAL"
print("All tests passed!")
