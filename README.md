# FortiEDR Scripts

This repository contains two scripts for interacting with FortiEDR:
- **List Events**: Retrieve events using different time filters.
- **Threat Hunting**: Perform threat-hunting queries based on categories, time periods, and filters.

---
## 1. Environment Variables Configuration (`.env`)

Before running the scripts, you need to create a `.env` file in the same directory as the scripts to store your FortiEDR API credentials.

Example `.env` file format:

```ini
FORTIEDR_USER=johndoe
FORTIEDR_PASS=password
FORTIEDR_HOST=fortixdrconnectca4.fortiedr.com
FORTIEDR_ORG=MyOrg
```

---
## 2. Install Required Dependencies

Before running the scripts, install the necessary Python packages using:

```bash
pip install fortiedr pandas tabulate python-dotenv
```

---
## 3. Running the Scripts

### List Events

This script allows you to retrieve events from FortiEDR using different time filters.

#### User Input Prompts:
- **Output Format**: `Do you want the raw JSON output or table format? (default: table): `
- **Max Items**: `Enter max number of items to display (or press Enter for no limit): `
- **Action Filter**: `Enter action filter (Block, SimulationBlock, Log) or press Enter for no filter: `
- **Time Selection**:
  - `Choose an option:
    1 - Last N days
    2 - Last X hours
    3 - Custom date range
    Enter your choice (1/2/3): `
  - If `1` is selected: `Enter the number of days: `
  - If `2` is selected: `Enter the number of hours: `
  - If `3` is selected: `Enter start date (YYYY-MM-DD): ` and `Enter end date (YYYY-MM-DD): `

Run the script with:

```bash
python list-events.py
```

### Threat Hunting

This script allows you to perform threat-hunting queries by specifying different filters.

#### User Input Prompts:
- **Output Format**: `Do you want the raw JSON output or table format? (default: table): `
- **Max Items**: `Enter max number of items to display (or press Enter for no limit): `
- **Category**: `Enter the category (Process, File, Registry, Network, Event Log, All) (default: no category): `
- **Time Selection**:
  - `Enter the time period (lastHour, last12hours, last24hours, last7days, last30days, custom) (default: no time period): `
  - If `custom` is selected: `Enter the start date (yyyy-MM-dd): `

Run the script with:

```bash
python threat-hunting.py
```
