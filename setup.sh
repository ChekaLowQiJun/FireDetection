#!/bin/bash

# Install Docker
if ! command -v docker &> /dev/null
then
    echo "Installing Docker..."
    brew install --cask docker
    open /Applications/Docker.app
    echo "Please complete Docker setup in the GUI, then press Enter to continue"
    read
fi

# Install AWS CLI
if ! command -v aws &> /dev/null
then
    echo "Installing AWS CLI..."
    brew install awscli
    aws configure
fi

# Verify installations
echo "Verifying installations..."
docker --version
aws --version

echo "Setup complete. You can now run ./deploy.sh"
