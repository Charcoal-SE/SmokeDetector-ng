# SmokeDetector-ng
[![Build Status](https://img.shields.io/travis/Charcoal-SE/SmokeDetector-ng.svg?label=travis)](https://travis-ci.org/Charcoal-SE/SmokeDetector-ng)
[![CircleCI](https://img.shields.io/circleci/project/github/Charcoal-SE/SmokeDetector-ng.svg?label=circle)](https://circleci.com/gh/Charcoal-SE/SmokeDetector-ng)
[![Build status](https://img.shields.io/appveyor/ci/quartata/SmokeDetector-ng/master.svg?label=appveyor)](https://ci.appveyor.com/project/quartata/smokedetector-ng)
[![codecov](https://img.shields.io/codecov/c/github/Charcoal-SE/SmokeDetector-ng/master.svg)](https://codecov.io/gh/Charcoal-SE/SmokeDetector-ng)
[![Code Climate](https://img.shields.io/codeclimate/github/Charcoal-SE/SmokeDetector-ng.svg)](https://codeclimate.com/github/Charcoal-SE/SmokeDetector-ng)
[![Dependency Status](https://www.versioneye.com/user/projects/58dd73dcd6c98d004405474f/badge.svg?style=flat-squared)](https://www.versioneye.com/user/projects/58dd73dcd6c98d004405474f)

## Setup

Retrieve and install depedencies:

    git clone --recursive https://github.com/Charcoal-SE/SmokeDetector-ng
    cd SmokeDetector-ng
    
    sudo pip3 install -r requirements.txt


Set up the database:

    cd bin
    python3 create_database.py
    cd ..


Fill out the sample `config/secrets-sample.json` and rename it to `config/secrets.json` and encrypt it:

    cd src
    python3 secrets.py ../config/secrets.json


Then start with either `python3 daemon.py` (restarts after failure) or `python3 entry.py`.
