#!/bin/bash

declare -A docker_functions_map=(
    ["functions/process_pilot_data"]="process-pilot-data"
    ["functions/notify"]="notify"
    ["functions/message-status"]="message-status"
)

changed_functions=""

set -x

if [ -z "$CHANGED_FOLDERS" ]; then
    changed_functions="null"
    echo "No files changed"
elif [[ "$CHANGED_FOLDERS" == *Shared* ]]; then
    echo "Shared folder changed, returning all functions"
    for key in "${!docker_functions_map[@]}"; do
        changed_functions+=" ${docker_functions_map[$key]}"
        echo "Adding in: ${docker_functions_map[$key]}"
    done
else
    echo "files changed $CHANGED_FOLDERS "
    for folder in $CHANGED_FOLDERS; do
      echo "Add this function in: ${folder} "
      echo "Add this which maps to: ${docker_functions_map[$folder]} "
      changed_functions+=" ${docker_functions_map[$folder]}"
    done
fi

# Format the output for the github matrix:
changed_functions_json=$(printf '["%s"]' "$(echo $changed_functions | sed 's/ /","/g')")

echo "Final list of functions to rebuild:"
echo "$changed_functions_json"

echo "FUNC_NAMES=$changed_functions_json" >> "$GITHUB_OUTPUT"
