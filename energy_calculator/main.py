from .tariffs_data import tariffs
from .utils import get_periods_consumption, get_rd_10_mean_price, get_rd_10_prices


def main():

    contracted_p1 = 3.0  # kW
    contracted_p2 = 3.0  # kW

    rd_10_prices_url = "https://www.mibgas.es/es/file-access/MIBGAS_Data_2022.xlsx?path=AGNO_2022/XLS"

    rd_10_prices = get_rd_10_prices(rd_10_prices_url)
    rd_10_mean_price = get_rd_10_mean_price(rd_10_prices)
    print(f"RD10 mean price: {rd_10_mean_price:.4f} €/kWh \n")

    file_path = "./data/consumo_periodo_30-08-2021_30-08-2022.csv"
    consumption_data = get_periods_consumption(file_path)

    # Print the consumption distribution
    print(f"Period 1 distribution: {consumption_data.p1_distribution:.1f} %")
    print(f"Period 1 consumtion: {consumption_data.consumption_p1:.1f} kWh")
    print(f"Period 2 distribution: {consumption_data.p2_distribution:.1f} %")
    print(f"Period 2 consumtion: {consumption_data.consumption_p2:.1f} kWh")
    print(f"Period 3 distribution: {consumption_data.p3_distribution:.1f} %")
    print(f"Period 3 consumtion: {consumption_data.consumption_p3:.1f} kWh")
    print(f"Total consumption: {consumption_data.total_consumption:.1f} kWh\n")

    # Get a list with the energy costs for each tariff
    tariffs_costs = [
        (
            t.name,
            t.calculate_electricity_cost(
                consumption_data, contracted_p1, contracted_p2, rd_10_mean_price
            ).total_cost,
        )
        for t in tariffs
    ]
    # Order the tarifs by energy cost
    tariffs_costs.sort(key=lambda x: x[1])
    # Print the results ordered by energy cost
    bestTariffCost = tariffs_costs[0][1]
    for tariff_name, tariff_cost in tariffs_costs:
        tariffCostDiff = tariff_cost - bestTariffCost
        print(f"{tariff_name} energy cost: {tariff_cost:.2f}€ (+{tariffCostDiff:.2f}€)")

    # Get the best tariffs with the RD10 included and not included
    best_rd_tariff = None
    best_non_rd_tariff = None
    for tariff_name, tariff_cost in tariffs_costs:
        for t in tariffs:
            if t.name == tariff_name:
                if t.rd_10_included and not best_rd_tariff:
                    best_rd_tariff = t
                elif not t.rd_10_included and not best_non_rd_tariff:
                    best_non_rd_tariff = t
                break
        if best_rd_tariff and best_non_rd_tariff:
            break

    assert best_rd_tariff and best_non_rd_tariff

    # Get the cost of the best tariffs
    best_rd_10_tariff_cost = best_rd_tariff.calculate_electricity_cost(
        consumption_data, contracted_p1, contracted_p2, rd_10_mean_price
    )
    best_non_rd_10_tariff_cost = best_non_rd_tariff.calculate_electricity_cost(
        consumption_data, contracted_p1, contracted_p2, rd_10_mean_price
    )

    # Calculate the RD10 threshold
    thRD10Price = (
        best_rd_10_tariff_cost.cost_without_taxes
        - best_non_rd_10_tariff_cost.energy_cost
        - best_non_rd_10_tariff_cost.power_cost
    ) / consumption_data.total_consumption
    print("")
    print(f"RD10 threshold: {thRD10Price:.4f} €/kWh")
