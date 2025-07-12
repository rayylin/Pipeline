from polygon import RESTClient

client = RESTClient("b5UCMzdBDke3aeFqLkfakPjG2xQbJcoW")

request = client.get_daily_open_close_agg(
    "AAPL",
    "2025-07-09",
    adjusted="true",
)

print(request)