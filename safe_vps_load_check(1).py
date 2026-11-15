#!/usr/bin/env python3
"""
Production-safe, bounded HTTP capacity check for a VPS you own.
Hard limits: <= 2 requests/second, <= 2 in-flight requests, <= 90 seconds,
<= 120 total requests. Stops early on overload signals.
Install: python -m pip install aiohttp
Run:     python safe_vps_load_check.py
"""

import asyncio
import time
from collections import deque
from datetime import datetime
from urllib.parse import urlparse

try:
    import aiohttp
except ImportError:
    print("Missing dependency. Install it with: python -m pip install aiohttp")
    raise SystemExit(1)

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Deliberately conservative production hard limits.
STAGES = [(0.5, 20), (1.0, 25), (1.5, 25), (2.0, 20)]  # RPS, seconds
MAX_RPS = 2.0
MAX_IN_FLIGHT = 2
MAX_REQUESTS = 120
MAX_DURATION = 90
TIMEOUT_SECONDS = 5
WINDOW = 10


def banner():
    print(CYAN + BOLD + r"""
  __  __  ___  ____  _____ ____  _   _
 |  \/  |/ _ \|  _ \|_   _/ ___|| | | |
 | |\/| | | | | | | | | | \___ \| |_| |
 | |  | | |_| | |_| | | |  ___) |  _  |
 |_|  |_|\___/|____/  |_| |____/|_| |_|
       BOUNDED VPS LOAD CHECK
""" + RESET)
    print(GREEN + "Green status • live stats • gradual ramp • auto-stop" + RESET)
    print("-" * 58)


def validate_url(raw):
    raw = raw.strip()
    if not raw.startswith(("https://", "http://")):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in ("https", "http") or not parsed.hostname:
        raise ValueError("Некорректный URL.")
    if parsed.username or parsed.password:
        raise ValueError("URL не должен содержать логин или пароль.")
    return raw


async def main():
    banner()
    print(YELLOW + "Только для VPS/сайта, которым ты владеешь или управляешь." + RESET)
    print("Жёсткие пределы: 2 запроса/с, 2 одновременных запроса, 90 с, 120 запросов.")
    target = validate_url(input("\nURL сайта: "))
    if input("Подтверди владение/разрешение (введи YES): ").strip() != "YES":
        print(RED + "Отменено." + RESET)
        return

    print("\nПлан нагрузки:")
    for rps, seconds in STAGES:
        print(f"  {rps:.1f} req/s × {seconds} s")
    print(YELLOW + "Это ограниченная проверка доступности, не тест на разрушение сайта." + RESET)
    if input("Начать? (yes/no): ").strip().lower() != "yes":
        print("Отменено.")
        return

    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
    connector = aiohttp.TCPConnector(limit=MAX_IN_FLIGHT, ssl=True)
    headers = {"User-Agent": "SafeVPSLoadCheck/1.0"}
    semaphore = asyncio.Semaphore(MAX_IN_FLIGHT)
    recent = deque(maxlen=WINDOW)
    all_latencies = []
    counts = {"ok": 0, "http_error": 0, "network_error": 0, "total": 0}
    stop_reason = None
    start = time.monotonic()
    last_slow = 0

    async with aiohttp.ClientSession(timeout=timeout, connector=connector,
                                     headers=headers) as session:

        async def one_request(number):
            nonlocal stop_reason, last_slow
            if stop_reason or counts["total"] >= MAX_REQUESTS:
                return
            async with semaphore:
                t0 = time.perf_counter()
                try:
                    async with session.get(target, allow_redirects=False) as resp:
                        # Do not download the response body.
                        resp.release()
                        ms = (time.perf_counter() - t0) * 1000
                        status = resp.status
                        all_latencies.append(ms)
                        counts["total"] += 1
                        if 200 <= status < 400:
                            counts["ok"] += 1
                            label, color = "OK", GREEN
                        else:
                            counts["http_error"] += 1
                            label, color = f"HTTP {status}", YELLOW
                        recent.append((status, ms))
                        print(f"{color}[{number:03d}] {label:<9} {ms:7.0f} ms | "
                              f"ok {counts['ok']} / errors "
                              f"{counts['http_error'] + counts['network_error']}{RESET}")
                        if status == 429:
                            stop_reason = "Сервер вернул HTTP 429 (ограничение запросов)."
                        elif status >= 500:
                            # Stop if >= 3 server errors among the last 10 responses.
                            if sum(1 for s, _ in recent if s >= 500) >= 3:
                                stop_reason = "Повторяющиеся HTTP 5xx."
                        if ms >= 5000:
                            last_slow += 1
                        else:
                            last_slow = 0
                        if last_slow >= 3:
                            stop_reason = "Три медленных ответа подряд (>= 5 секунд)."
                except Exception as exc:
                    counts["total"] += 1
                    counts["network_error"] += 1
                    recent.append((0, TIMEOUT_SECONDS * 1000))
                    print(f"{RED}[{number:03d}] ERROR {type(exc).__name__}: {exc}{RESET}")
                    if counts["network_error"] >= 3:
                        stop_reason = "Три сетевые ошибки."
                    if len(recent) >= 5:
                        failures = sum(1 for s, _ in recent if s == 0 or s >= 500)
                        if failures / len(recent) >= 0.4:
                            stop_reason = "Доля ошибок в последних ответах достигла 40%."

        number = 0
        try:
            for rps, seconds in STAGES:
                if stop_reason or counts["total"] >= MAX_REQUESTS:
                    break
                rps = min(rps, MAX_RPS)
                print(CYAN + f"\nЭтап: {rps:.1f} req/s, до {seconds} секунд" + RESET)
                interval = 1.0 / rps
                stage_end = time.monotonic() + seconds
                next_at = time.monotonic()
                while time.monotonic() < stage_end:
                    if stop_reason or counts["total"] >= MAX_REQUESTS:
                        break
                    if time.monotonic() - start >= MAX_DURATION:
                        stop_reason = "Достигнут общий лимит времени."
                        break
                    delay = next_at - time.monotonic()
                    if delay > 0:
                        await asyncio.sleep(delay)
                    number += 1
                    await one_request(number)
                    next_at += interval
                if stop_reason:
                    break
        except KeyboardInterrupt:
            stop_reason = "Остановлено пользователем."

    elapsed = time.monotonic() - start
    print("\n" + "-" * 58)
    print(BOLD + "ИТОГИ" + RESET)
    print(f"Всего запросов: {counts['total']}")
    print(f"{GREEN}Успешные ответы: {counts['ok']}{RESET}")
    print(f"{YELLOW}HTTP-ошибки: {counts['http_error']}{RESET}")
    print(f"{RED}Сетевые ошибки: {counts['network_error']}{RESET}")
    print(f"Фактическая скорость: {counts['total'] / elapsed:.2f} req/s" if elapsed else "Фактическая скорость: 0")
    if all_latencies:
        print(f"Среднее время ответа: {sum(all_latencies)/len(all_latencies):.0f} ms")
        print(f"Минимум / максимум: {min(all_latencies):.0f} / {max(all_latencies):.0f} ms")
    print(f"Длительность: {elapsed:.1f} s")
    print("Причина завершения: " + (stop_reason or "План завершён."))
    print("Время: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(GREEN + "Проверка завершена." + RESET)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
