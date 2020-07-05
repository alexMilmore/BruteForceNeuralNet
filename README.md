# BruteForceNeuralNet
Generates and tests and compares different neural network models. Currently supports image classification with linear models. All data is stored on an MySQL database.

# Setup
A MySQL server must be set up to store data inside.\
A database to store the data is then created using createDatabase.sh\
Tests to be performed are set up in the database using uploadTests.py\
To run these tests classifierTester.py is run.\
All of these processes are run one after the other if fullTest.sh is used, however it does not currently store data, so you have to log in 3 times.

# Considerations
This program was originally designed to classify healthy and sick patients from medical scans. The more general uses of this program are somewhat untested.
