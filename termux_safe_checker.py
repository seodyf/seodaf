#!/usr/bin/env python3
"""
Termux Safe Network Checker
Sequential, bounded HTTP checks for systems you own or are authorized to test.
No threads, no flooding, maximum 10 requests, minimum 2-second interval.
"""

import time
import urllib.request
import urllib.error
from urllib.parse import urlparse
from datetime import datetime

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def banner():
    print(CYAN + BOLD + r"""
  _______ _____ _____ __  __
 |__   __|  ___|  __ \  \/  |
    | |  | |__ | |__) | \  /
    | |  |  __||  _  /  |  |
    | |  | |___| | \ \  |  |
    |_|  |_____|_|  \_\ |_|
       SAFE NETWORK CHECKER
""" + RESET)
    print(GREEN + "  Sequential checks • capped requests • no threads" + RESET)
    print("-" * 54)


def normalize_url(raw):
    raw = raw.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Укажи корректный адрес, например https://example.com")
    return raw


def main():
    banner()
    print(YELLOW + "Используй только свой сервер или ресурс, на тестирование которого есть разрешение." + RESET)
    target = normalize_url(input("\nАдрес сервера: "))

    confirm = input("Подтверди разрешение на проверку (введи YES): ").strip()
    if confirm != "YES":
        print(RED + "Проверка отменена." + RESET)
        return

    try:
        count = int(input("Количество проверок (1–10, максимум 10): ").strip())
    except ValueError:
        print(RED + "Нужно ввести целое число." + RESET)
        return

    if not 1 <= count <= 10:
        print(RED + "Допустимо от 1 до 10 проверок." + RESET)
        return

    print(f"\n{CYAN}Цель:{RESET} {target}")
    print(f"{CYAN}Проверок:{RESET} {count} | {CYAN}Интервал:{RESET} не менее 2 сек | {CYAN}Потоки:{RESET} 1")
    print("-" * 54)

    ok = 0
    errors = 0
    latencies = []
    statuses = []

    for i in range(1, count + 1):
        req = urllib.request.Request(
            target,
            headers={"User-Agent": "TermuxSafeNetworkChecker/1.0"},
            method="GET",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                # Read only a tiny amount; this is a reachability/status check.
                response.read(1)
                status = response.status
                elapsed = (time.perf_counter() - started) * 1000
                ok += 1
                latencies.append(elapsed)
                statuses.append(status)
                print(f"{GREEN}[{i:02d}/{count:02d}] OK  HTTP {status}  {elapsed:.0f} ms{RESET}")
        except urllib.error.HTTPError as exc:
            elapsed = (time.perf_counter() - started) * 1000
            errors += 1
            statuses.append(exc.code)
            print(f"{YELLOW}[{i:02d}/{count:02d}] HTTP {exc.code}  {elapsed:.0f} ms{RESET}")
        except Exception as exc:
            errors += 1
            elapsed = (time.perf_counter() - started) * 1000
            print(f"{RED}[{i:02d}/{count:02d}] ERROR: {type(exc).__name__}: {exc}{RESET}")

        if i < count:
            time.sleep(2)

    print("\n" + "-" * 54)
    print(BOLD + "ИТОГОВАЯ СТАТИСТИКА" + RESET)
    print(f"{GREEN}Успешные ответы: {ok}{RESET}")
    print(f"{RED}Ошибки / HTTP-ошибки: {errors}{RESET}")
    print(f"Всего проверок: {count}")
    if latencies:
        print(f"Среднее время ответа: {sum(latencies) / len(latencies):.0f} ms")
        print(f"Минимальное время: {min(latencies):.0f} ms")
        print(f"Максимальное время: {max(latencies):.0f} ms")
    if statuses:
        print("HTTP-коды: " + ", ".join(map(str, statuses)))
    print("Завершено: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(GREEN + "\nПроверка завершена. Запросы выполнялись последовательно." + RESET)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + YELLOW + "Остановлено пользователем." + RESET)
