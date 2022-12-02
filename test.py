
def data_split(data: str, size=2, hex=True) -> list:
    if hex:
        return [int(data[x-size:x], 16) for x in range(size, len(data)+size, size)]
    else:
        return [data[x-size:x] for x in range(size, len(data)+size, size)]


print(data_split('0004085751524559595555', 4, hex=False))
