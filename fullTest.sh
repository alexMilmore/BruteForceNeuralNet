#!/bin/bash
# create database
./createDatabase.sh
# upload tests to database
python uploadTests.py
# run machine learning tests in database
python classifierTester.py
