# SmokeDetector-ng
[![Code Climate](https://codeclimate.com/github/Charcoal-SE/SmokeDetector-ng/badges/gpa.svg)](https://codeclimate.com/github/Charcoal-SE/SmokeDetector-ng)

## Setup

Retrieve and install depedencies:

    git clone --recursive https://github.com/Charcoal-SE/SmokeDetector-ng
    cd SmokeDetector-ng
    
    sudo pip3 install -r requirements.txt
    
Fill out the sample `config/secrets.json` and encrypt it:

    cd src
    python3 secrets.py ../config/secrets.json

Then start with either `python3 daemon.py` (restarts after failure) or `python3 entry.py`.
