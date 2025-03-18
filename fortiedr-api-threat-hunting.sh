#!/bin/bash

# Search parameters
CATEGORY="Process" # Process, File, Registry, Network, Event Log, All
DEVICES=()
TIME="lastHour"
ITEMS_PER_PAGE=1

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found!"
    exit 1
fi

# Verify required environment variables
if [[ -z "$FORTIEDR_USER" || -z "$FORTIEDR_PASS" || -z "$FORTIEDR_HOST" || -z "$FORTIEDR_ORG" ]]; then
    echo "Error: Missing required environment variables in .env file!"
    exit 1
fi

# Encode credentials in Base64
AUTH_TOKEN=$(echo -n "${FORTIEDR_ORG}\\${FORTIEDR_USER}:${FORTIEDR_PASS}" | base64)

# Define API URL
API_URL="https://${FORTIEDR_HOST}/management-rest/threat-hunting/search"

# Construct JSON request body
REQUEST_BODY="{\"time\": \"$TIME\", \"itemsPerPage\": $ITEMS_PER_PAGE"

# Add category if defined
if [ -n "$CATEGORY" ]; then
    REQUEST_BODY+=" ,\"category\": \"$CATEGORY\""
fi

REQUEST_BODY+=" }"

# Display curl command in a single line
CURL_COMMAND="curl -s -X POST -H \"Authorization: Basic ${AUTH_TOKEN}\" -H \"Content-Type: application/json\" -d '${REQUEST_BODY}' \"${API_URL}\""

echo -e "\n$CURL_COMMAND\n"

# Ask user if they want full response or summary
echo -e "\nDo you want to display the full response or a summary?"
echo "1) Full response"
echo "2) Summary"
read -r CHOICE

# Execute API request
RESPONSE=$(eval $CURL_COMMAND)

# Process user choice
if [[ "$CHOICE" -eq 1 ]]; then
    echo -e "\nFull response:\n"
    echo "$RESPONSE" | jq .
elif [[ "$CHOICE" -eq 2 ]]; then
    echo -e "\nSummary:\n"
    echo "$RESPONSE" | jq '[.[] | {
        Category: .Category,
        CollectorVersion: .Device.CollectorVersion,
        Name: .Device.Name,
        OS: .Device.OS,
        OSVersion: .Device.OSVersion,
        Type: .Type,
        EventProcessTime: .EventProcessTime,
        ID: .ID
    } ]'
else
    echo "Invalid choice. Displaying full response by default."
    echo "$RESPONSE" | jq .
fi
