import os
import json
import fortiedr
import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def authenticate():
    """ Authenticate to FortiEDR using credentials from .env """
    authentication = fortiedr.auth(
        user=os.getenv("FORTIEDR_USER"),
        passw=os.getenv("FORTIEDR_PASS"),
        host=os.getenv("FORTIEDR_HOST"),
        org=os.getenv("FORTIEDR_ORG")
    )

    if not authentication['status']:
        print("Authentication failed:", authentication['data'])
        exit()

    return authentication

def get_events(method, firstSeenFrom=None, firstSeenTo=None, action_filter=None, max_items=None, output_format="table"):
    """ Fetch events with optional filters for action type, max items per page, and output format """
    
    params = {}
    
    if firstSeenFrom and firstSeenTo:
        params["firstSeenFrom"] = firstSeenFrom
        params["firstSeenTo"] = firstSeenTo
    if action_filter:
        params["actions"] = action_filter
    if max_items:
        params["itemsPerPage"] = max_items
    
    # Print the API request in red
    print("\n\033[91m" + f"API Request: {params}" + "\033[0m\n")
    
    data = method.list_events(**params)
    display_events(data, output_format)

def display_events(data, output_format):
    """ Display event data in a formatted table or as JSON """
    if data['status']:
        if output_format == "json":
            print(json.dumps(data, indent=2))
        else:
            table_data = []
            for index, entry in enumerate(data["data"], start=1):
                table_data.append([
                    index,  # Line number
                    entry["eventId"],
                    entry["process"],
                    entry["firstSeen"],
                    entry["lastSeen"],
                    entry["classification"],
                    entry["collectors"][0]["device"] if entry["collectors"] else "N/A",
                    entry["action"]
                ])

            headers = ["#", "Event ID", "Process", "First Seen", "Last Seen", "Classification", "Device", "Action"]
            df = pd.DataFrame(table_data, columns=headers)
            print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    else:
        print("Error in fetching data.")

def main():
    """ Main function to execute authentication and event retrieval """
    authentication = authenticate()
    print("\nAuthentication successful!")

    method = fortiedr.Events()

    output_format = input("\nDo you want the raw JSON output or table format? (default: table): ").strip().lower() or "table"

    max_items = input("\nEnter max number of items to display (or press Enter for no limit): ").strip()
    max_items = int(max_items) if max_items.isdigit() else None
    
    action_filter = input("\nEnter action filter (Block, SimulationBlock, Log) or press Enter for no filter: ").strip() or None

    print("\nChoose an option:")
    print("1 - Last N days")
    print("2 - Last X hours")
    print("3 - Custom date range")
    choice = input("\nEnter your choice (1/2/3): ")
    
    if choice == "1":
        days = int(input("\nEnter the number of days: "))
        get_events(method, (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action_filter, max_items, output_format)

    elif choice == "2":
        hours = int(input("\nEnter the number of hours: "))
        get_events(method, (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action_filter, max_items, output_format)

    elif choice == "3":
        start_date = input("\nEnter start date (YYYY-MM-DD): ")
        end_date = input("\nEnter end date (YYYY-MM-DD): ")
        get_events(method, f"{start_date} 00:00:00", f"{end_date} 23:59:59", action_filter, max_items, output_format)

    else:
        print("\nNo date filter applied. Fetching all available events.")
        get_events(method, action_filter=action_filter, max_items=max_items, output_format=output_format)

if __name__ == "__main__":
    main()