#Bank Of Joe(program)

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Optional

# -------- Domain Model --------

@dataclass
class Account:
    number: int
    owner: str
    balance: float = 0.0
    daily_limit: float = 0.0
    # Track how much has been withdrawn today:
    last_withdraw_date: date = field(default_factory=date.today)
    withdrawn_today: float = 0.0

    def _rollover_if_new_day(self) -> None:
        """Reset daily withdrawal counter if we've crossed into a new day."""
        today = date.today()
        if self.last_withdraw_date != today:
            self.last_withdraw_date = today
            self.withdrawn_today = 0.0

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        self._rollover_if_new_day()

        if amount > self.balance:
            raise ValueError(f"Insufficient funds. Balance: {self.balance:.2f}")

        # Check daily limit only if limit is set (> 0)
        if self.daily_limit > 0:
            remaining = self.daily_limit - self.withdrawn_today
            if amount > remaining:
                raise ValueError(
                    f"Daily limit exceeded. Remaining today: {remaining:.2f}"
                )

        self.balance -= amount
        self.withdrawn_today += amount

    def apply_interest(self, rate_percent: float) -> float:
        """Apply interest immediately; returns interest amount credited."""
        if rate_percent < 0:
            raise ValueError("Rate cannot be negative.")
        interest = self.balance * (rate_percent / 100.0)
        self.balance += interest
        return interest

    def __str__(self) -> str:
        self._rollover_if_new_day()
        lim = f"{self.daily_limit:.2f}" if self.daily_limit > 0 else "No limit"
        rem = (
            f"{self.daily_limit - self.withdrawn_today:.2f}"
            if self.daily_limit > 0
            else "—"
        )
        return (
            f"Account #{self.number} | Owner: {self.owner} | "
            f"Balance: ₹{self.balance:.2f} | Daily limit: {lim} | "
            f"Remaining today: {rem}"
        )


class Bank:
    def __init__(self, starting_number: int = 1001):
        self._accounts: Dict[int, Account] = {}
        self._next = starting_number

    # --- Account lifecycle ---

    def open_account(
        self, owner: str, initial_deposit: float = 0.0, daily_limit: float = 0.0
    ) -> Account:
        if not owner.strip():
            raise ValueError("Owner name required.")
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative.")
        if daily_limit < 0:
            raise ValueError("Daily limit cannot be negative.")

        acc = Account(
            number=self._next, owner=owner.strip(), balance=0.0, daily_limit=daily_limit
        )
        self._next += 1

        if initial_deposit > 0:
            acc.deposit(initial_deposit)

        self._accounts[acc.number] = acc
        return acc

    def close_account(self, number: int) -> Account:
        acc = self._accounts.get(number)
        if not acc:
            raise KeyError(f"Account #{number} not found.")
        if acc.balance != 0:
            raise ValueError("Account balance must be zero before closing.")
        del self._accounts[number]
        return acc

    def get(self, number: int) -> Optional[Account]:
        return self._accounts.get(number)

    def list_accounts(self) -> Dict[int, Account]:
        return dict(self._accounts)


# -------- CLI Utilities --------

def read_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number.")

def read_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a valid integer.")

def pause():
    input("\nPress Enter to continue...")

def print_header(title: str):
    print("\n" + "_" * 70)
    print(title)
    print("_" * 70)

def show_account(acc: Account):
    print(acc)


# -------- Screens --------

def screen_open_account(bank: Bank):
    print_header("Open New Account")
    owner = input("Owner name: ").strip()
    initial = read_float("Initial deposit (₹): ")
    limit = read_float("Daily withdrawal limit (₹, 0 for no limit): ")
    try:
        acc = bank.open_account(owner, initial, limit)
        print("\n Account opened successfully!")
        show_account(acc)
    except ValueError as e:
        print(f"{e}")
    pause()

def screen_close_account(bank: Bank):
    print_header("Close Account")
    number = read_int("Account number: ")
    try:
        acc = bank.get(number)
        if not acc:
            print("Account not found.")
        else:
            print("Current state:")
            show_account(acc)
            confirm = input(
                "Close this account? (requires zero balance) [y/N]: "
            ).strip().lower()
            if confirm == "y":
                bank.close_account(number)
                print("Account closed.")
            else:
                print("Cancelled.")
    except (KeyError, ValueError) as e:
        print(f"{e}")
    pause()

def screen_deposit(bank: Bank):
    print_header("Deposit")
    number = read_int("Account number: ")
    amount = read_float("Amount (₹): ")
    acc = bank.get(number)
    if not acc:
        print("Account not found.")
    else:
        try:
            acc.deposit(amount)
            print("Deposit successful.")
            show_account(acc)
        except ValueError as e:
            print(f"{e}")
    pause()

def screen_withdraw(bank: Bank):
    print_header("Withdraw")
    number = read_int("Account number: ")
    amount = read_float("Amount (₹): ")
    acc = bank.get(number)
    if not acc:
        print("Account not found.")
    else:
        try:
            acc.withdraw(amount)
            print("Withdrawal successful.")
            show_account(acc)
        except ValueError as e:
            print(f"{e}")
    pause()

def screen_interest(bank: Bank):
    print_header("Apply Interest")
    number = read_int("Account number: ")
    rate = read_float("Rate (%): ")
    acc = bank.get(number)
    if not acc:
        print("Account not found.")
    else:
        try:
            interest = acc.apply_interest(rate)
            print(f"Interest ₹{interest:.2f} credited.")
            show_account(acc)
        except ValueError as e:
            print(f"{e}")
    pause()

def screen_lookup(bank: Bank):
    print_header("Lookup Account")
    number = read_int("Account number: ")
    acc = bank.get(number)
    if not acc:
        print("Account not found.")
    else:
        show_account(acc)
    pause()

def screen_list(bank: Bank):
    print_header("All Accounts")
    accts = bank.list_accounts()
    if not accts:
        print("No accounts yet.")
    else:
        for acc in accts.values():
            print(acc)
    pause()


# -------- Main Menu --------

def main_menu():
    bank = Bank()  # fresh in-memory bank
    while True:
        print_header("BANK OF JOE")
        print("1) Open account")
        print("2) Close account")
        print("3) Deposit")
        print("4) Withdraw")
        print("5) Apply interest")
        print("6) Lookup account")
        print("7) List all accounts")
        print("0) Exit")
        choice = input("\nChoose: ").strip()

        if choice == "1":
            screen_open_account(bank)
        elif choice == "2":
            screen_close_account(bank)
        elif choice == "3":
            screen_deposit(bank)
        elif choice == "4":
            screen_withdraw(bank)
        elif choice == "5":
            screen_interest(bank)
        elif choice == "6":
            screen_lookup(bank)
        elif choice == "7":
            screen_list(bank)
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice.")
            pause()

if __name__ == "__main__":
    main_menu()
