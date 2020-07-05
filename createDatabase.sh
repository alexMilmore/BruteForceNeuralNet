#!/bin/bash
# Create database
echo "please input the name of the database"
read databaseName

SQLCommand="
CREATE DATABASE $databaseName;
USE $databaseName

CREATE TABLE inputData(
  dataset varchar(255) PRIMARY KEY,
  filepath varchar(255)
);

CREATE TABLE IDKey(
  testID int(255) PRIMARY KEY,
  modelArchitecture varchar(255),
  dataSet varchar(255),
  imageDimentions int(8),
  epochs int(8),
  batchSize int(8),
  tested boolean,
  error boolean,
  FOREIGN KEY (dataSet) REFERENCES inputData(dataSet)
);

CREATE TABLE overview(
  testID int(255) PRIMARY KEY,
  loss float(8),
  predictionAccuracy float(8),
  healthyPredictionAccuracy float(8),
  sickPredictionAccuracy float(8),
  FOREIGN KEY (testID) REFERENCES IDKey(testID)
);

CREATE TABLE trainingLogs(
  testID int(255),
  fold int(8),
  epoch int(8),
  loss float(8),
  FOREIGN KEY (testID) REFERENCES IDKey(testID)
);

CREATE TABLE testingLogs(
  testID int(255),
  fold int(8),
  modelOutput varchar(255),
  correctAnswer varchar(255),
  FOREIGN KEY (testID) REFERENCES IDKey(testID)
  /*TODO; ADD REFERENCE TO SPECIFIC IMAGE IN TEST*/
);
"

mysql -u root -p -e "$SQLCommand"
echo "Database created"

# Specify dataPaths
echo "input dataset name"
read dataset
echo "input filepath of dataset"
read filepath

SQLCommand2="
USE $databaseName
INSERT INTO inputData (dataset, filepath)
VALUES ($dataset, $filepath);"

mysql -u root -p -e "$SQLCommand2"
echo "Dataset initialised"
