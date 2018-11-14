#!/usr/bin/env bash

if [[ ! -d SourceMeter-8.2.0-x64-linux ]] && [[ ! -f SourceMeter-8.2.0-x64-linux.zip ]]; then
    echo "Unable to find SourceMeter!"
fi

if [[ ! -d SourceMeter-8.2.0-x64-linux ]] && [[ -f SourceMeter-8.2.0-x64-linux.zip ]]; then
    unzip SourceMeter-8.2.0-x64-linux.zip -d SourceMeter-8.2.0-x64-linux
    rm SourceMeter-8.2.0-x64-linux.zip
    pip install pandas
    echo "Setup is complete!"
fi

if [[ -d SourceMeter-8.2.0-x64-linux ]] && [[ ! -f SourceMeter-8.2.0-x64-linux.zip ]]; then
    pip install pandas
    echo "SourceMeter directory is already set up!"
fi

if [[ -d SourceMeter-8.2.0-x64-linux ]] && [[ -f SourceMeter-8.2.0-x64-linux.zip ]]; then
    pip install pandas
    rm SourceMeter-8.2.0-x64-linux.zip
    echo "Cleaning up SourceMeter .zip archive!!"
fi
