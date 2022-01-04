from tariffs_data import tariffs
from utils import get_periods_consumption

contracted_p1 = 3.0  # kW
contracted_p2 = 3.0  # kW

file_path = "./data/test_weekend.csv"
consumption_data = get_periods_consumption(file_path)

# Print the consumption distribution
print(f"Period 1 distribution: {consumption_data.p1_distribution:.1f} %")
print(f"Period 2 distribution: {consumption_data.p2_distribution:.1f} %")
print(f"Period 3 distribution: {consumption_data.p3_distribution:.1f} %")
print(f"Total consumption: {consumption_data.total_consumption:.1f} kWh")

# Get a list with the energy costs for each tariff
tariffs_costs = [
    (t.name, t.calculate_energy_cost(consumption_data, contracted_p1, contracted_p2))
    for t in tariffs
]
# Order the tarifs by energy cost
tariffs_costs.sort(key=lambda x: x[1])
# Print the results ordered by energy cost
for tariff_name, tariff_cost in tariffs_costs:
    print(f"{tariff_name} energy cost: {tariff_cost:.2f} €")
