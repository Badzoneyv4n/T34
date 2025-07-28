# bot/utils/balance_manager.py

class BalanceManager:
    """
    Manages risk per trade by calculating base amount using your balance,
    desired risk percentage and martingale strategy.
    """

    def __init__(self, balance: float, risk_per_signal: float = 0.10, martingale_levels: int = 3):
        """
        :param balance: Current account balance.
        :param risk_per_signal: Fraction of balance to risk per signal (0.05 means 5%).
        :param martingale_levels: Number of martingale levels (base + retrades).
        """
        self.balance = balance
        self.risk_per_signal = risk_per_signal
        self.martingale_levels = martingale_levels

    def max_exposure_units(self) -> int:
        """
        Sum the units for martingale series: 1, 2, 4, 8, ...
        Example: levels=3 => 1+2+4+8 = 15
        """
        return sum([2 ** i for i in range(self.martingale_levels + 1)])

    def calc_base_amount(self) -> float:
        """
        Calculates the safest base bet based on risk % and available balance.
        Enforces minimum stake of $1 for PocketOption.
        """
        max_risk_amount = self.balance * self.risk_per_signal
        exposure_units = self.max_exposure_units()
        base_unit = max_risk_amount / exposure_units

        # Enforce broker min stake
        final_base = max(1.0, round(base_unit, 2))
        return final_base

    def update_balance(self, new_balance: float):
        """
        Updates your balance for next calculation.
        """
        self.balance = new_balance

    def summary(self) -> str:
        """
        Quick debug summary for logging.
        """
        return (
            f"[BalanceManager] Balance=${self.balance:.2f} | "
            f"Risk={self.risk_per_signal*100:.1f}% | "
            f"MG Levels={self.martingale_levels} | "
            f"Exposure Units={self.max_exposure_units()} | "
            f"Base Bet=${self.calc_base_amount():.2f}"
        )
