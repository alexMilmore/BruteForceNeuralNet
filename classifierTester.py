import matplotlib.pyplot as plt
import dataHandler as dh
import neuralModel as nModel
import pandas as pd
import os
import gc
import genArchitecture as genModel
import matplotlib.pyplot as plt
import databaseConnect as dbConnect
import architectureTranslate as archTran
import numpy as np

# set random seeds
from numpy.random import seed;
seed(1);
from tensorflow import set_random_seed;
set_random_seed(2);

### This program takes data and compares different neural network architectures
#       to see which one is the best

# create database connection
cursor = dbConnect.dbCursor();

# Import tests from the server
testParameters = cursor.readTests();

# create object to handle data importing
inputHandler = dh.dataHandler(2, {'HV':'0', 'PA':'1', 'PT':'1'})

# Flags for loading new data
currentDataPath = "";
currentDimentions = 0;

for entry in testParameters:
    fold = 1;

    architecture = archTran.textToArchitecture(entry['modelArchitecture']);

    # load images from database and generate testing and training data from them
    # imageDimentions sets the resolution of each image
    # inputHandler loads the data in full resolution and then can generate
    # testing and training data at smaller resolutions without reloading data.
    # This is done to prevent having to reload all images when testing different resolutions
    imagePath = cursor.lookUpImagePath(entry['dataSet']);
    if (currentDataPath != imagePath):
        inputHandler.updateData(imagePath, {'HV':'0', 'PA':'1', 'PT':'1'});
        inputHandler.genMachineLearningData((entry['imageDimentions'], entry['imageDimentions']));
        currentDataPath = imagePath;
        currentDimentions = entry['imageDimentions'];
    elif (entry['imageDimentions'] != currentDimentions):
        inputHandler.genMachineLearningData((entry['imageDimentions'], entry['imageDimentions']));
        currentDimentions = entry['imageDimentions'];

    # initialise neural net with settings
    inputShape = (entry['imageDimentions'], entry['imageDimentions'], 1);
    classModel = nModel.classifier(architecture, inputHandler);

    # Train neural net
    classModel.train(entry['epochs'], entry['batchSize']);
    classModel.summary();

    # Upload overview metrics to the database
    # TODO make upload depenent on the number of categories
    print ("Uploading overview to server");
    currentMetrics = classModel.overviewMetrics();
    cursor.inputOverviewToServer(entry['testID'], currentMetrics['loss'], \
    currentMetrics['totalAccuracy'], currentMetrics['class1Accuracy'], currentMetrics['class2Accuracy']);

    # Upload training metrics to the database
    print ("Uploading training metrics to server");
    trainingMetrics = classModel.getTrainingData();
    for i in range(0, len(trainingMetrics['loss'])):
        # TODO add val_loss
        cursor.inputTrainDataToServer(entry['testID'], fold, i + 1, trainingMetrics['loss'][i]);

    # Upload testing metrics to the database
    print ("Uploading testing metrics to server");
    testMetrics = classModel.getTestingData();
    for i in range(0, len(testMetrics['predictions'])):
        cursor.inputTestDataToServer(entry['testID'], fold, str(testMetrics['predictions'][i]), str(testMetrics['answers'][i]));

    # TODO uncomment this stuff when code is done
    # mark test as completed
    #cursor.markCompleted(entry['testID']);

    # Delete model to free memory;
    del classModel;
    gc.collect();
    # Clear any graphs
    plt.clf()
