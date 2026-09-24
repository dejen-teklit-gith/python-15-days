"""Day 02 — Functions as values: password policy, retry/backoff, command router."""
import time
from typing import Callable

Rule = Callable[[str], bool]


# ── 1. Password policy engine: rules are just functions ─────────────────────
def has_digit(pw: str) -> bool:
    return any(ch.isdigit() for ch in pw)


def has_upper(pw: str) -> bool:
    return any(ch.isupper() for ch in pw)


def has_symbol(pw: str) -> bool:
    return any(not ch.isalnum() for ch in pw)


def make_min_length_rule(n: int) -> Rule:
    """Closure: the returned function REMEMBERS n."""
    def rule(pw: str) -> bool:
        return len(pw) >= n
    rule.__name__ = f"min_length_{n}"
    return rule


POLICY: list[Rule] = [make_min_length_rule(10), has_digit, has_upper, has_symbol]


def check_password(pw: str, policy: list[Rule] = POLICY) -> list[str]:
    """Return the names of failed rules (empty list = valid)."""
    return [rule.__name__ for rule in policy if not rule(pw)]


# ── 2. Retry with exponential backoff: a function that takes a function ─────
def retry(action: Callable[[], str], attempts: int = 4, base_delay: float = 0.05) -> str:
    for attempt in range(1, attempts + 1):
        try:
            return action()
        except ConnectionError as err:
            if attempt == attempts:
                raise
            delay = base_delay * 2 ** (attempt - 1)
            print(f"  attempt {attempt} failed ({err}); retrying in {delay:.2f}s")
            time.sleep(delay)
    raise RuntimeError("unreachable")


def make_flaky_service(fail_times: int) -> Callable[[], str]:
    """Simulates a network call that fails the first `fail_times` calls."""
    calls = 0

    def call() -> str:
        nonlocal calls          # modify the enclosing variable (the 'E' in LEGB)
        calls += 1
        if calls <= fail_times:
            raise ConnectionError("timeout")
        return f"200 OK after {calls} calls"
    return call


# ── 3. Command router with structural pattern matching ──────────────────────
def route(command: str) -> str:
    match command.split():
        case ["help"]:
            return "commands: add <a> <b> | greet <name> | quit"
        case ["add", a, b] if a.lstrip("-").isdigit() and b.lstrip("-").isdigit():
            return str(int(a) + int(b))
        case ["greet", *names] if names:
            return "Hello, " + " & ".join(names) + "!"
        case ["quit" | "exit"]:
            return "bye"
        case _:
            return f"unknown command: {command!r}"


# ── Bonus: the mutable default trap ─────────────────────────────────────────
def add_tag_buggy(tag, tags=[]):          # noqa: B006  (intentional bug)
    tags.append(tag)
    return tags


def add_tag_fixed(tag, tags=None):
    tags = [] if tags is None else tags
    tags.append(tag)
    return tags


if __name__ == "__main__":
    print("=== Password policy ===")
    for pw in ["hello", "Hello12345", "Hello-12345!"]:
        failed = check_password(pw)
        print(f"{pw:<14} {'✅ OK' if not failed else '❌ ' + ', '.join(failed)}")

    print("\n=== Retry with backoff ===")
    print(retry(make_flaky_service(fail_times=2)))

    print("\n=== Command router ===")
    for cmd in ["help", "add 2 40", "greet Ana Ben", "dance", "exit"]:
        print(f"> {cmd:<14} {route(cmd)}")

    print("\n=== Mutable default trap ===")
    print("buggy:", add_tag_buggy("a"), add_tag_buggy("b"))   # shares one list!
    print("fixed:", add_tag_fixed("a"), add_tag_fixed("b"))
