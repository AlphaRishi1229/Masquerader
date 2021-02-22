#!/bin/bash

echo "Welcome To Masquerader Shared Service Manager."
echo ""
OUTPUT="$1"
echo "Masquerader Shared Service: $OUTPUT"
echo ""

if [ "$USER" == "root" ]; then
    echo "Error: Please Run This Script Without Root."
    exit 1
else
    echo "Running Script Using User: $USER"
    echo ""
fi

echo "Operating System Detected: $OSTYPE"
echo ""
if [ "$OSTYPE" == "linux-gnu" ]; then
    DATA_DIRECTORIES=("/home/$USER/fynd/docker-data/postgresql/db")
elif [[ "$OSTYPE" == "adarwin"* ]]; then
    DATA_DIRECTORIES=("/Users/$USER/fynd/docker-data/postgresql/db")
else
    echo "Error: Sorry, This Script Only Supports Linux And Mac Os."
    exit 1
fi

if [ "$OUTPUT" = "start" ]; then
    echo "Creating/Verifying Required Data Directories:"
    echo "--------------------------------------------------------------------"
    for i in "${DATA_DIRECTORIES[@]}"
        do
            if [ -d "$i" ]; then
                echo "Data directory: $i"
                echo "Already Exists, Reusing It."
            else
                echo "Data directory: $i"
                echo "Doesn't Exists, Creating It."
                mkdir -p $i
            fi
        done
    echo "--------------------------------------------------------------------"
    echo "Data Directories Creation/Verification Completed."
    echo ""

    echo "Exporting Data Directories To Operating System."
    export fyndPostgresqlVolume=${DATA_DIRECTORIES[0]}
    echo "Successfully Exported Data Directories To Operating System."
    echo ""

    echo "Setting Up 'fyndnet' For Connecting Containers."
    OUTPUT="$(docker network list)"
    if echo "$OUTPUT" | grep -q "fyndnet"; then
        echo "Existing Network Found, Reusing It.";
        echo ""
    else
        echo "Creating New Network.";
        docker network create fyndnet > /dev/null 2>&1
        echo "Successfully Created New Network"
        echo ""
    fi

    if [ "$OSTYPE" = "linux-gnu" ]; then
        echo "Shutting Down Existing Local Services."
        sudo service postgresql stop > /dev/null 2>&1
        echo "Successfully Shut Down Existing Local Services."
        echo ""
    fi

    echo "Starting Shared Services:"
    echo "--------------------------------------------------------------------"
    docker-compose up -d
    echo "--------------------------------------------------------------------"
    echo "Successfully Started Shared Services."
    echo ""

elif [ "$OUTPUT" = "stop" ]; then
    # Added below export to avoid warning from docker-compose.
    export fyndPostgresqlVolume=${DATA_DIRECTORIES[0]}
    echo "Shutting Down Shared Services:"
    echo "--------------------------------------------------------------------"
    docker-compose down
    echo "--------------------------------------------------------------------"
    echo "Successfully In Shutting Down Shared Services."

elif [ "$OUTPUT" = "status" ]; then
    echo "Checking Shared Service Status:"
    echo "--------------------------------------------------------------------"
    RUNNING_CONT="$(docker ps)"
    if echo "$RUNNING_CONT" | grep -q "postgresql"; then
        echo "PostgreSQL: Up"
    else
        echo "PostgreSQL: Down"
    fi
    echo "--------------------------------------------------------------------"
    echo "Successfully Checked Status Shared Services."
    echo ""

else
    echo "Error: Invalid Command, Provide 'start', 'stop' or 'status' As Arguement."
fi
