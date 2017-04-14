# SmokeDetector-ng
[![Build Status](https://travis-ci.org/Charcoal-SE/SmokeDetector-ng.svg?branch=master)](https://travis-ci.org/Charcoal-SE/SmokeDetector-ng)
[![CircleCI](https://circleci.com/gh/Charcoal-SE/SmokeDetector-ng.svg?style=shield)](https://circleci.com/gh/Charcoal-SE/SmokeDetector-ng)
[![Build status](https://ci.appveyor.com/api/projects/status/lqwxh106c5k8vefb?svg=true)](https://ci.appveyor.com/project/quartata/smokedetector-ng)
[![Code Climate](https://codeclimate.com/github/Charcoal-SE/SmokeDetector-ng/badges/gpa.svg)](https://codeclimate.com/github/Charcoal-SE/SmokeDetector-ng)
[![Dependency Status](https://www.versioneye.com/user/projects/58dd73dcd6c98d004405474f/badge.svg?style=flat-square)](https://www.versioneye.com/user/projects/58dd73dcd6c98d004405474f)

## Setup

Retrieve and install depedencies:

    git clone --recursive https://github.com/Charcoal-SE/SmokeDetector-ng
    cd SmokeDetector-ng
    
    sudo pip3 install -r requirements.txt
    
Fill out the sample `config/secrets.json` and encrypt it:

    cd src
    python3 secrets.py ../config/secrets.json

Then start with either `python3 daemon.py` (restarts after failure) or `python3 entry.py`.
