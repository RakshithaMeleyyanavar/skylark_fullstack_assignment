from tools import get_deals

res = get_deals(status="Won")
print("Total Deals Found in get_deals(status='Won'):", res["total_deals_found"])
print("Sum Masked Value:", res["sum_masked_value"])
print("Data Caveat:", res["data_caveat"])
