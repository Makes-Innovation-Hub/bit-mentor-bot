#!/bin/bash

# Check if Docker Hub username and environment are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <docker_hub_username> <env>"
    echo "env: 'dev' or 'prod'"
    exit 1
fi

DOCKER_HUB_USERNAME="$1"
ENVIRONMENT="$2"

IMAGE_NAME="bit-mentor-bot"
TAG="latest"
CONTAINER_NAME="bit-mentor-bot-container"

# Versioning logic: Read the current version from version.txt
VERSION_FILE="version.txt"
if [ ! -f "$VERSION_FILE" ]; then
    echo "1.0.0" > "$VERSION_FILE"
fi

VERSION_TAG=$(cat "$VERSION_FILE")

# Increment the version (assumes semantic versioning)
IFS='.' read -r major minor patch <<< "$VERSION_TAG"
patch=$((patch + 1))
VERSION_TAG="$major.$minor.$patch"

# Update the version.txt with the new version
echo "$VERSION_TAG" > "$VERSION_FILE"

# Set the environment file path
ENV_FILE_PATH="$(cd "$(dirname "$0")" && pwd)/.env_dev"

# Adjust for Windows path
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    ENV_FILE_PATH=$(cygpath -w "$ENV_FILE_PATH")
fi

# Check if the environment file exists
if [ ! -f "$ENV_FILE_PATH" ]; then
    echo "Environment file '$ENV_FILE_PATH' not found."
    exit 1
fi

echo "Using environment file at: '$ENV_FILE_PATH'"

# Build Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

if [ $? -eq 0 ]; then
    echo "Docker image built successfully."

    docker tag $IMAGE_NAME:$TAG $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION_TAG

    echo "Pushing Docker image to Docker Hub..."
    docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION_TAG

    if [ $? -eq 0 ]; then
        echo "Docker image pushed to Docker Hub successfully."

        # Determine the Docker Compose file based on the environment
        if [ "$ENVIRONMENT" == "dev" ]; then
            COMPOSE_FILE="docker-compose.dev.yml"
        elif [ "$ENVIRONMENT" == "prod" ]; then
            COMPOSE_FILE="docker-compose.prod.yml"
        else
            echo "Invalid environment specified. Use 'dev' or 'prod'."
            exit 1
        fi

        echo "Running Docker container with Docker Compose ($COMPOSE_FILE)..."
        docker-compose -f $COMPOSE_FILE up -d
        if [ $? -eq 0 ]; then
            echo "Docker container is running."
        else
            echo "Failed to start Docker container."
        fi
    else
        echo "Failed to push Docker image to Docker Hub."
    fi
else
    echo "Docker image build failed."
fi
