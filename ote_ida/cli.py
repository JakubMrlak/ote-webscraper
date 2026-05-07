import argparse
import logging
from datetime import date, datetime
from ote_ida.downloader import fetch_auction, fetch_range, SESSIONS


def parse_date(s: str) -> date:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Neplatné datum: {s}, očekáváný formát: YYYY-MM-DD")


def main():
    parser = argparse.ArgumentParser(
        description="Stahování výsledků vnitrodenních aukcí OTE IDA"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Příkaz: stáhni jeden den a session
    single = subparsers.add_parser("fetch", help="Stáhni jednu aukci")
    single.add_argument("session", choices=SESSIONS, help="IDA1, IDA2 nebo IDA3")
    single.add_argument("date", type=parse_date, help="Datum ve formátu YYYY-MM-DD")

    # Příkaz: stáhni rozsah datumů
    range_cmd = subparsers.add_parser("fetch-range", help="Stáhni rozsah datumů")
    range_cmd.add_argument("date_from", type=parse_date, help="Od data YYYY-MM-DD")
    range_cmd.add_argument("date_to", type=parse_date, help="Do data YYYY-MM-DD")
    range_cmd.add_argument(
        "--sessions",
        nargs="+",
        choices=SESSIONS,
        default=SESSIONS,
        help="Sessions ke stažení (výchozí: všechny)"
    )

    # Logování
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Úroveň logování"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    if args.command == "fetch":
        fetch_auction(args.session, args.date)

    elif args.command == "fetch-range":
        if args.date_from > args.date_to:
            parser.error("date_from musí být před date_to")
        fetch_range(args.date_from, args.date_to, args.sessions)


if __name__ == "__main__":
    main()