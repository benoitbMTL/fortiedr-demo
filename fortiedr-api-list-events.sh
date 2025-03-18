#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found!"
    echo -e "\nExpected .env file format:"
    echo "--------------------------"
    echo "FORTIEDR_USER=your_username"
    echo "FORTIEDR_PASS=your_password"
    echo "FORTIEDR_HOST=your_host"
    echo "FORTIEDR_ORG=your_organization"
    exit 1
fi

# Verify required environment variables
if [[ -z "$FORTIEDR_USER" || -z "$FORTIEDR_PASS" || -z "$FORTIEDR_HOST" || -z "$FORTIEDR_ORG" ]]; then
    echo "Error: Missing required environment variables in .env file!"
    echo -e "\nExpected .env file format:"
    echo "--------------------------"
    echo "FORTIEDR_USER=your_username"
    echo "FORTIEDR_PASS=your_password"
    echo "FORTIEDR_HOST=your_host"
    echo "FORTIEDR_ORG=your_organization"
    exit 1
fi

# Check if jq is installed, install if necessary
if ! command -v jq &> /dev/null; then
    echo "Installing jq..."
    sudo apt update && sudo apt install jq -y
else
    echo "jq is already installed."
fi

# Encode credentials in Base64
AUTH_TOKEN=$(echo -n "${FORTIEDR_ORG}\\${FORTIEDR_USER}:${FORTIEDR_PASS}" | base64)

# Masked Auth Token for display
MASKED_AUTH_TOKEN=$(echo "$AUTH_TOKEN" | sed 's/./*/g')

API_URL="https://${FORTIEDR_HOST}/management-rest/events/list-events"

# Define actions to query
FILTERS=("Block" "SimulationBlock" "Log")

# ANSI color codes
RED='\033[0;31m'
NC='\033[0m' # No color

# Loop through each filter and execute the request
for action in "${FILTERS[@]}"; do
    echo -e "\n----------------------------------------"
    echo "Filter used: actions=${action}"
    
    # Construct the curl request (masked for display)
    CURL_CMD="curl -s -H \"Authorization: Basic ${MASKED_AUTH_TOKEN}\" \"${API_URL}?itemsPerPage=1&actions=${action}\""
    
    echo "Full CURL request:"
    echo "${CURL_CMD}"
    
    # Execute the actual request with the real token
    RESPONSE=$(curl -s -H "Authorization: Basic ${AUTH_TOKEN}" "${API_URL}?itemsPerPage=1&actions=${action}")

    # Check if the response contains an error message
    if echo "${RESPONSE}" | jq empty 2>/dev/null; then
        # Valid JSON response, apply jq filtering
        echo -e "\nFiltered output:"
        echo "${RESPONSE}" | jq '.[] | {eventId, process, classification, device: .collectors[0].device, action}'
    else
        # Invalid JSON, display raw response in RED
        echo -e "\n${RED}Raw API response:${NC}"
        echo "${RESPONSE}"
    fi
done

echo -e "\nScript completed."
