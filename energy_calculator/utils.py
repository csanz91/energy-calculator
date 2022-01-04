from dataclasses import dataclass
import math

from holidays_es import Province
import pandas as pd


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


@dataclass(frozen=True)
class TariffData:
    name: str
    energy_cost_p1: float  # €/kWh
    energy_cost_p2: float  # €/kWh
    energy_cost_p3: float  # €/kWh
    power_cost_p1: float  # €/kW/day
    power_cost_p2: float  # €/kW/day

    def calculate_energy_cost(
        self, consumption: DataConsumption, contracted_p1: float, contracted_p2: float
    ) -> float:
        return (
            consumption.consumption_p1 * self.energy_cost_p1
            + consumption.consumption_p2 * self.energy_cost_p2
            + consumption.consumption_p3 * self.energy_cost_p3
            + consumption.num_days
            * (self.power_cost_p1 * contracted_p1 + self.power_cost_p2 * contracted_p2)
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

    # P1 consumption: from 10:00 to 14:00 and from 18:00 to 22:00
    consumption_p1 = df.loc[
        ~df.weekend
        & ~df.holiday
        & ((df.Hora >= 10) & (df.Hora < 14) | (df.Hora >= 18) & (df.Hora < 22))
    ].AE_kWh.sum()

    # P2 consumption: from 08:00 to 10:00, from 14:00 to 18:00 and from 22:00 to 24:00
    consumption_p2 = df.loc[
        ~df.weekend
        & ~df.holiday
        & (
            (df.Hora >= 8) & (df.Hora < 10)
            | (df.Hora >= 14) & (df.Hora < 18)
            | (df.Hora >= 22) & (df.Hora < 24)
        )
    ].AE_kWh.sum()

    # P3 consumption: from 00:00 to 08:00, weekend days and holidays
    consumption_p3 = df.loc[
        df.weekend | df.holiday | (df.Hora >= 0) & (df.Hora < 8)
    ].AE_kWh.sum()

    data = DataConsumption(
        consumption_p1=consumption_p1,
        consumption_p2=consumption_p2,
        consumption_p3=consumption_p3,
        num_days=len(df.groupby("Fecha")),
    )

    # Make sure we have divided the different consumption periods correctly
    assert math.isclose(data.total_consumption, df.AE_kWh.sum())

    return data
