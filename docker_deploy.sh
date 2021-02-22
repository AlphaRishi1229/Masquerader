#!/bin/bash

echo "------------------------------------------------------------------------"
echo "Starting Local Deployment."
echo "------------------------------------------------------------------------"
ACTION="$1"
BUILD="$2"
NOCACHE="$3"
# Change APP_NAME With Repository Name.
# Change SHARED SERVICES With The List Of SHARED SERVICES Required.
# Available SHARED SERVICES Are: ["mysql", "mongo", "redis", "kafka", "zookeeper"]
APP_NAME="masquerader"
SHARED_SERVICES=("postgresql")
echo "Repository Name: $APP_NAME"
echo "List Of Shared Services: ${SHARED_SERVICES[@]}"
echo ""
echo ""

# -----------------------------------------------------------------------------
# DO NOT MAKE CHANGES BELOW.
# -----------------------------------------------------------------------------
echo "------------------------------------------------------------------------"
echo "Checking If 'docker-composer.yml' Exist."
echo "------------------------------------------------------------------------"
COMPOSE_YML_EXISTS=$([ -f "docker-compose.yml" ] && echo "yes")
if [ "$COMPOSE_YML_EXISTS" != "yes" ]; then
    echo "Error: We Could Not Find 'docker-compose.yml' In '$APP_NAME'."
    exit 1
else
    echo "We Could Find 'docker-compose.yml' In '$APP_NAME'."
fi
echo ""
echo ""

if [ "$ACTION" == "start" ]; then
    echo "--------------------------------------------------------------------"
    echo "Starting Shared Services At '/local_development/shared_services.sh'"
    echo "--------------------------------------------------------------------"
    cd local_development
    ./shared_services.sh start
    cd ..
    echo ""

    echo "------------------------------------------------------------------------"
    echo "Checking Availability Of Shared Services."
    echo "------------------------------------------------------------------------"
    CAN_RUN="yes"
    RUNNING_CONT="$(docker ps)"
    for i in "${SHARED_SERVICES[@]}"
        do
            if echo "$RUNNING_CONT" | grep -q "$i"; then
                echo "$i: Up"
            else
                echo "$i: Down"
                CAN_RUN="no"
            fi
        done
    echo ""
    echo ""

    echo "------------------------------------------------------------------------"
    echo "Starting Services At '$APP_NAME'."
    echo "------------------------------------------------------------------------"
    if [ "$CAN_RUN" = "yes" ]; then
        if [ "$BUILD" = "build" ]; then
            if [ "$NOCACHE" = "nocache" ]; then
                docker-compose build --no-cache
                docker-compose up
            else
                docker-compose up --build
            fi
        else
            docker-compose up
        fi
    else
        echo "Error: We Could Not Run Shared Services."
    fi

elif [ "$ACTION" = "stop" ]; then
    echo "--------------------------------------------------------------------"
    echo "Stoping Services At '$APP_NAME'"
    echo "--------------------------------------------------------------------"
    docker-compose down
    echo ""
    echo ""

    echo "--------------------------------------------------------------------"
    echo "Stoping Shared Services At '/local_development/shared_services.sh'"
    echo "--------------------------------------------------------------------"
    cd local_development
    ./shared_services.sh stop
    cd ..

elif [ "$ACTION" = "status" ]; then
    echo "--------------------------------------------------------------------"
    echo "Status Of Shared Services At '/local_development/shared_services.sh'"
    echo "--------------------------------------------------------------------"
    cd local_development
    ./shared_services.sh status
    cd ..
    echo ""

    echo "--------------------------------------------------------------------"
    echo "Status Of Services At '$APP_NAME'"
    echo "--------------------------------------------------------------------"
    RUNNING_CONT="$(docker ps)"
    if echo "$RUNNING_CONT" | grep -q "masquerader"; then
        echo "masquerader: Up"
    else
        echo "masquerader: Down"
    fi

else
    echo "Error: Invalid Command, Provide 'start', 'stop' or 'status' As Arguement."
fi
