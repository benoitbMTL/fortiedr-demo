import os
import json
import fortiedr
import pandas as pd
from datetime import datetime
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

def main():
    """ Main function to execute authentication and event retrieval """
    authentication = authenticate()
    print("\nAuthentication successful!")

    method = fortiedr.ThreatHunting()

    # Ask user for preferences with improved formatting
    output_format = input("\nDo you want the raw JSON output or table format? (default: table): ").strip().lower() or "table"
    max_items = input("\nEnter max number of items to display (or press Enter for no limit): ").strip()
    max_items = int(max_items) if max_items.isdigit() else None
    category = input("\nEnter the category (Process, File, Registry, Network, Event Log, All) (default: no category): ").strip()
    
    time_period = input("\nEnter the time period (lastHour, last12hours, last24hours, last7days, last30days, custom) (default: no time period): ").strip()

    # Initialize from_time only if custom time period is chosen
    from_time = ""
    if time_period.lower() == "custom":
        from_time = input("\nEnter the start date (yyyy-MM-dd): ").strip()

    # Prepare search parameters
    search_params = {}

    if max_items:
        search_params['itemsPerPage'] = int(max_items)
    if category:
        search_params['category'] = category
    if time_period.lower() == "custom" and from_time:
        search_params['fromTime'] = f"{from_time} 00:00:00"
        search_params['time'] = "custom"  # 'time' must be 'custom' when 'fromTime' is specified
    elif time_period and time_period.lower() != "custom":
        search_params['time'] = time_period  # Use predefined time periods only

    # Print the API request in red
    print("\n\033[91m" + f"API Request: {search_params}" + "\033[0m\n")

    # Perform the search
    data = method.search(**search_params)

    if data['status']:
        if output_format == "json":
            # Print raw JSON output
            print(json.dumps(data, indent=2))
        else:
            # Extract relevant fields for table format
            table_data = []
            for index, event in enumerate(data['data'], start=1):
                source_process = event['Source'].get('Process', {})
                command_line = source_process.get('CommandLine', 'N/A')
                user_info = source_process.get('User', {})
                username = user_info.get('Username', 'N/A')
                target_path = event['Target'].get('File', {}).get('Path', 'N/A')

                table_data.append([
                    index,  # Line number
                    datetime.fromtimestamp(event['Time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                    event['Type'],
                    event['Device']['Name'],
                    source_process.get('Name', 'N/A'),
                    command_line,
                    target_path,
                    username
                ])

            # Define headers for the table
            headers = ["#", "Time", "Type", "Device Name", "Process Name", "Command Line", "Target Path", "User"]

            # Create a DataFrame
            df = pd.DataFrame(table_data, columns=headers)

            # Display formatted table output in terminal
            print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    else:
        print("Failed to retrieve data:", data)

if __name__ == "__main__":
    main()
