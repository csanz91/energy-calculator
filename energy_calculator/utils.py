import math
from dataclasses import dataclass

import pandas as pd
from holidays_es import Province


def get_rd_10_prices(excelFile) -> pd.DataFrame:
    return pd.read_excel(
        excelFile, sheet_name="PGN_RD_10_2022", names=["date", "price"], index_col=0
    )


def get_rd_10_mean_price(rd_10_prices):
    # Get the mean of the last 30 days
    return rd_10_prices.iloc[:30].price.mean() / 1000.0


@dataclass(frozen=True)
class DataConsumption:
    consumption_p1: float  # kWh
    consumption_p2: float  # kWh
    consumption_p3: float  # kWh
    num_days: int

    @property
    def total_consumption(self) -> float:
        return self.consumption_p1 + self.consumption_p2 + self.consumption_p3

    @property
    def p1_distribution(self) -> float:
        return self.consumption_p1 / self.total_consumption * 100.0

    @property
    def p2_distribution(self) -> float:
        return self.consumption_p2 / self.total_consumption * 100.0

    @property
    def p3_distribution(self) -> float:
        return self.consumption_p3 / self.total_consumption * 100.0


@dataclass()
class ElectricityCost:
    energy_cost: float  # €/kWh
    power_cost: float  # €/kWh
    rd_10_cost: float  # €/kWh
    tax_base: float = 0.0  # €
    electricity_cost_tax: float = 0.0  # €
    tax: float = 0.0  # €
    total_cost: float = 0.0  # €

    def __post_init__(self):
        ELECTRICITY_TAX = 0.5  # %
        GENERAL_TAX = 5.0  # %
        ENERGY_MONITOR_COST_PER_DAY = 0.02663  # %

        electricity_cost = self.cost_without_taxes
        energy_monitor_cost = 366 * ENERGY_MONITOR_COST_PER_DAY
        self.electricity_cost_tax = electricity_cost * ELECTRICITY_TAX / 100.0
        self.tax_base = (
            electricity_cost + self.electricity_cost_tax + energy_monitor_cost
        )
        self.tax = self.tax_base * GENERAL_TAX / 100.0
        self.total_cost = self.tax_base + self.tax

    @property
    def cost_without_taxes(self) -> float:
        return self.energy_cost + self.power_cost + self.rd_10_cost

    def __str__(self) -> str:
        return f"""Energy cost: {self.energy_cost:.2f} € \nPower cost: {self.power_cost:.2f} € \nRD10 cost: {self.rd_10_cost:.2f} € \nEnergy cost: {self.energy_cost:.2f} € \nTotal cost: {self.total_cost:.2f} €"""


@dataclass(frozen=True)
class TariffData:
    name: str
    energy_cost_p1: float  # €/kWh
    energy_cost_p2: float  # €/kWh
    energy_cost_p3: float  # €/kWh
    power_cost_p1: float  # €/kW/day
    power_cost_p2: float  # €/kW/day
    rd_10_included: bool  # The tarrif includes the RD 10 2022 into the prices

    def calculate_electricity_cost(
        self,
        consumption: DataConsumption,
        contracted_p1: float,
        contracted_p2: float,
        rd_10_mean_price: float,
    ) -> ElectricityCost:

        power_cost = consumption.num_days * (
            self.power_cost_p1 * contracted_p1 + self.power_cost_p2 * contracted_p2
        )

        energy_cost = (
            consumption.consumption_p1 * self.energy_cost_p1
            + consumption.consumption_p2 * self.energy_cost_p2
            + consumption.consumption_p3 * self.energy_cost_p3
        )

        if self.rd_10_included:
            rd_10_cost = 0.0
        else:
            rd_10_cost = consumption.total_consumption * rd_10_mean_price

        return ElectricityCost(
            energy_cost=energy_cost,
            power_cost=power_cost,
            rd_10_cost=rd_10_cost,
        )


def get_periods_consumption(file_path: str) -> DataConsumption:
    """
    Calculates the energy periods consumption.
    Returns:
        DataConsumption instance
    """

    # Read the file
    df = pd.read_csv(filepath_or_buffer=file_path, sep=";", decimal=",")

    # Parse the column "Fecha" as a datetime object
    df.Fecha = pd.to_datetime(df.Fecha, format="%d/%m/%Y")

    # Get the National Holidays
    year = df.Fecha.iloc[0].year
    national_holidays = Province(name="madrid", year=year).national_holidays()

    # Create a new column indicating if the day is a weekend day or not
    df["weekend"] = df.Fecha.dt.dayofweek // 5 == 1
    # Create a new column indicating if the day was a holiday day or not
    df["holiday"] = df.Fecha.isin(national_holidays)

    # Make the hours start from 0
    df.Hora = df.Hora - 1

    energyColumn = "Consumo_kWh"
    if energyColumn not in df.columns:
        energyColumn = "AE_kWh"

    # P1 consumption: from 10:00 to 14:00 and from 18:00 to 22:00
    consumption_p1 = df.loc[
        ~df.weekend
        & ~df.holiday
        & ((df.Hora >= 10) & (df.Hora < 14) | (df.Hora >= 18) & (df.Hora < 22))
    ][energyColumn].sum()

    # P2 consumption: from 08:00 to 10:00, from 14:00 to 18:00 and from 22:00 to 24:00
    consumption_p2 = df.loc[
        ~df.weekend
        & ~df.holiday
        & (
            (df.Hora >= 8) & (df.Hora < 10)
            | (df.Hora >= 14) & (df.Hora < 18)
            | (df.Hora >= 22) & (df.Hora < 24)
        )
    ][energyColumn].sum()

    # P3 consumption: from 00:00 to 08:00, weekend days and holidays
    consumption_p3 = df.loc[df.weekend | df.holiday | (df.Hora >= 0) & (df.Hora < 8)][
        energyColumn
    ].sum()

    data = DataConsumption(
        consumption_p1=consumption_p1,
        consumption_p2=consumption_p2,
        consumption_p3=consumption_p3,
        num_days=len(df.groupby("Fecha")),
    )

    # Make sure we have divided the different consumption periods correctly
    assert math.isclose(data.total_consumption, df[energyColumn].sum())

    return data
