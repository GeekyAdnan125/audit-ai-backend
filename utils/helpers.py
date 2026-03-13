
def safe_float(value):
    try:
        return float(value)
    except:
        return None
