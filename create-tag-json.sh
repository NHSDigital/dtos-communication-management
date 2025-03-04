#!/bin/bash

# Get the current date and time
current_date=$(date +"%Y-%m-%d")
current_time=$(date +"%H:%M:%S")

# Create the JSON content
json_content=$(cat <<EOF
{
  "date": "$current_date",
  "time": "$current_time"
}
EOF
)

# Write the JSON content to a file
echo "$json_content" > ./src/notify/tag.json

echo "JSON file './src/notify/tag.json' created with the current date and time."

