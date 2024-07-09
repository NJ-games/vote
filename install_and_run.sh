#!/bin/bash

# List of required libraries
libraries=("flask")

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Installing Python3..."
    sudo apt update
    sudo apt install -y python3 python3-pip
else
    echo "Python3 is already installed."
fi

# Check and install pip if not installed
if ! command -v pip3 &> /dev/null
then
    echo "pip3 is not installed. Installing pip3..."
    sudo apt install -y python3-pip
else
    echo "pip3 is already installed."
fi

# Install required libraries
for library in "${libraries[@]}"
do
    if ! pip3 show $library &> /dev/null
    then
        echo "Installing $library..."
        pip3 install $library
    else
        echo "$library is already installed."
    fi
done

# Run the app.py
python3 app.py
