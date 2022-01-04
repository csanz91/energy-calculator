import unittest

from energy_calculator.utils import get_periods_consumption, TariffData

P1_TEST_CONS = 21.2
P2_TEST_CONS = 20.2
P3_TEST_CONS = 3.6
ALL_DAY_CONS = P1_TEST_CONS + P2_TEST_CONS + P3_TEST_CONS

CONTRACTED_P1 = 3.0
CONTRACTED_P2 = 5.0

TARIFF = TariffData(
    name="Tariff 1",
    energy_cost_p1=0.3,
    energy_cost_p2=0.2,
    energy_cost_p3=0.1,
    power_cost_p1=0.1,
    power_cost_p2=0.05,
)


class TestHolidayEnergyData(unittest.TestCase):
    def setUp(self) -> None:
        self.consumption_data = get_periods_consumption("./data/test_holiday.csv")

    def test_p1_cons(self):
        self.assertEqual(self.consumption_data.consumption_p1, 0.0)

    def test_p2_cons(self):
        self.assertEqual(self.consumption_data.consumption_p2, 0.0)

    def test_p3_cons(self):
        self.assertAlmostEqual(self.consumption_data.consumption_p3, ALL_DAY_CONS)

    def test_p1_distribution(self):
        self.assertEqual(self.consumption_data.p1_distribution, 0.0)

    def test_p2_distribution(self):
        self.assertEqual(self.consumption_data.p2_distribution, 0.0)

    def test_p3_distribution(self):
        self.assertEqual(self.consumption_data.p3_distribution, 100.0)


class TestWeekendEnergyData(unittest.TestCase):
    def setUp(self) -> None:
        self.consumption_data = get_periods_consumption("./data/test_weekend.csv")

    def test_p1_cons(self):
        self.assertEqual(self.consumption_data.consumption_p1, 0.0)

    def test_p2_cons(self):
        self.assertEqual(self.consumption_data.consumption_p2, 0.0)

    def test_p3_cons(self):
        self.assertAlmostEqual(self.consumption_data.consumption_p3, ALL_DAY_CONS)

    def test_p1_distribution(self):
        self.assertEqual(self.consumption_data.p1_distribution, 0.0)

    def test_p2_distribution(self):
        self.assertEqual(self.consumption_data.p2_distribution, 0.0)

    def test_p3_distribution(self):
        self.assertEqual(self.consumption_data.p3_distribution, 100.0)


class TestWeekdayEnergyData(unittest.TestCase):
    def setUp(self) -> None:
        self.consumption_data = get_periods_consumption("./data/test_weekday.csv")

    def test_p1_cons(self):
        self.assertAlmostEqual(self.consumption_data.consumption_p1, P1_TEST_CONS)

    def test_p2_cons(self):
        self.assertAlmostEqual(self.consumption_data.consumption_p2, P2_TEST_CONS)

    def test_p3_cons(self):
        self.assertAlmostEqual(self.consumption_data.consumption_p3, P3_TEST_CONS)

    def test_p1_distribution(self):
        per = P1_TEST_CONS / ALL_DAY_CONS * 100
        self.assertAlmostEqual(self.consumption_data.p1_distribution, per)

    def test_p2_distribution(self):
        per = P2_TEST_CONS / ALL_DAY_CONS * 100
        self.assertAlmostEqual(self.consumption_data.p2_distribution, per)

    def test_p3_distribution(self):
        per = P3_TEST_CONS / ALL_DAY_CONS * 100
        self.assertAlmostEqual(self.consumption_data.p3_distribution, per)


class TestHolidayEnergyCost(unittest.TestCase):
    def setUp(self) -> None:
        self.consumption_data = get_periods_consumption("./data/test_holiday.csv")

    def test_energy_cost(self):
        energy_cost = TARIFF.calculate_energy_cost(
            self.consumption_data, CONTRACTED_P1, CONTRACTED_P2
        )

        self.assertEqual(
            energy_cost,
            ALL_DAY_CONS * TARIFF.energy_cost_p3
            + CONTRACTED_P1 * TARIFF.power_cost_p1
            + CONTRACTED_P2 * TARIFF.power_cost_p2
        )


class TestWeekendEnergyCost(unittest.TestCase):
    def setUp(self) -> None:
        self.consumption_data = get_periods_consumption("./data/test_weekend.csv")

    def test_energy_cost(self):
        energy_cost = TARIFF.calculate_energy_cost(
            self.consumption_data, CONTRACTED_P1, CONTRACTED_P2
        )

        self.assertEqual(
            energy_cost,
            ALL_DAY_CONS * TARIFF.energy_cost_p3
            + CONTRACTED_P1 * TARIFF.power_cost_p1
            + CONTRACTED_P2 * TARIFF.power_cost_p2,
        )


class TestWeekdayEnergyCost(unittest.TestCase):
    def setUp(self) -> None:
        self.consumption_data = get_periods_consumption("./data/test_weekday.csv")

    def test_energy_cost(self):
        energy_cost = TARIFF.calculate_energy_cost(
            self.consumption_data, CONTRACTED_P1, CONTRACTED_P2
        )

        self.assertAlmostEqual(
            energy_cost,
            P1_TEST_CONS * TARIFF.energy_cost_p1
            + P2_TEST_CONS * TARIFF.energy_cost_p2
            + P3_TEST_CONS * TARIFF.energy_cost_p3
            + CONTRACTED_P1 * TARIFF.power_cost_p1
            + CONTRACTED_P2 * TARIFF.power_cost_p2,
        )
