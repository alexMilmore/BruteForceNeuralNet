import numpy as np
import os
from tqdm import tqdm
import cv2
import random
from sklearn.utils import shuffle
from sklearn.preprocessing import OneHotEncoder
import pandas as pd

### Reading data functions
def imread(category, image, imagePath, shape, includeSides):
    path = os.path.join(imagePath,image)  # create path to dogs and cats
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE);
    if (includeSides == 0):
        image = image[0:400,0:400];
    image = cv2.resize(image, shape);
    image = np.asarray(image);
    return [image, category];

def createData(path, size, label, limit, includeSides):
    print(path)
    print("loading " + label + " data")

    data = [];
    count = 0;
    filecount = 0;

    for imageFile in tqdm(os.listdir(path)):
        if filecount > limit:
            break

        # Label depending on the name of the image
        if (imageFile.find("HV") != -1):
            data.append(imread('H', imageFile, path, size, includeSides));
            filecount += 1;
        elif (imageFile.find("PA") != -1) or (imageFile.find("PT") != -1):
            data.append(imread('P', imageFile, path, size, includeSides));
            filecount += 1;
        else:
            print("");
            print("Unidintified file: " + imageFile);
            print("");

    # Randomize data for later input into neural net
    data = shuffle(data, random_state = 0);
    return np.asarray(data);

def preprocessImages(images):
    # Remove mean from set of images
    avgImg = findAverageImg(images);
    images = removeAverage(images, avgImg);
    # normalize variance from 0~255 to 0~1
    images = images.astype('float32') / 255;
    avgImg = avgImg.astype('float32') / 255;

    return images, avgImg;

# Loads and reshapes into useful training data from filepath
# filePath: specifies the folders with the images
# imageSideLength: all images are squares, this specifies the side length of the square
# imageNumberLimit: max images the function will load
# All images projections of 3D volume scans are a 400*400px
# front projection with 400*200 side projections one function loads with With
# one loads without
#TODO; this is fucking garbage code
def loadTrainingData(filePath, imageSideLength, imageNumberLimit):
    ### Creating data
    trainingData = createData(filePath, (imageSideLength, imageSideLength), "training", imageNumberLimit, 0);
    images = [];
    classifications = [];

    for data, categories in trainingData:
        images.append(data);
        classifications.append(categories);

    images = np.asarray(images);
    classifications = np.asarray(classifications);

    # Add dimention in X data so that keras can read it correctly
    images = images[..., np.newaxis];

    # Preprocess images
    images, average = preprocessImages(images);

    classifications = pd.DataFrame(classifications, columns = ["Type"]);

    encoder = OneHotEncoder(sparse = False);
    classifications = encoder.fit_transform(classifications);

    return [images, average, classifications];

def loadTrainingDataWithSides(filePath, imageSideLength, imageNumberLimit):
    ### Creating data
    trainingData = createData(filePath, (imageSideLength, imageSideLength), "training", imageNumberLimit, 1);

    images = [];
    classifications = [];

    for data, categories in trainingData:
        images.append(data);
        classifications.append(categories);

    images = np.asarray(images);
    classifications = np.asarray(classifications);

    classifications = pd.DataFrame(classifications, columns = ["Type"]);

    encoder = OneHotEncoder(sparse = False);
    classifications = encoder.fit_transform(classifications);

    # Add dimention in X data so that keras can read it correctly
    images = images[..., np.newaxis];

    # Preprocess images
    images, average = preprocessImages(images);

    return [images, average, classifications];

############ Normalizing data ################################
# Calculate the average image in the dataset
def findAverageImg(data):
    sumImg = np.zeros(data[0].shape, dtype = np.double);
    numOfImages = data.shape[0]
    for i in range(0, numOfImages):
        sumImg = sumImg + data[i];

    sumImg = sumImg/numOfImages
    return sumImg;

# If given an average image, remove it from each image
def removeAverage(data, average):
    newData = np.copy(data);
    newData = newData.astype(np.double);
    numOfImages = data.shape[0]
    for i in range(0, numOfImages):
        newData[i] = newData[i] - average.astype(int);
        newData[i][newData[i] < 0] = 0;
    return newData;

# If given an average image, add it to each image
def restoreAverage(data, average):
    newData = np.copy(data);
    newData = newData.astype(np.double);
    numOfImages = data.shape[0]
    for i in range(0, numOfImages):
        newData[i] = newData[i] + average.astype(int);
        newData[i][newData[i] > 255] = 255;
    return newData;

'''
# for testing this bit of code
import matplotlib.pyplot as plt
filePath = "/home/alex/Documents/dataset/mipDataBest"
data = loadTrainingData(filePath, 50, 100);
images, labels = data;
avg = findAverageImg(images);
plt.imshow(np.reshape(images[0], (50,50)))
plt.show();
meanLess = removeAverage(images, avg);
plt.imshow(np.reshape(meanLess[0], (50,50)))
plt.show();
withMean = restoreAverage(images, avg);
plt.imshow(np.reshape(withMean[0], (50,50)))
plt.show();
'''
