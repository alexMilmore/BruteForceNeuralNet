import numpy as np
import os
from tqdm import tqdm
import cv2
import random
from sklearn.utils import shuffle
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
import pandas as pd

class dataHandler:
    def __init__(self, numOfCatagories, catagoryLabels):
        self.datapoints = 0;
        self.numOfCatagories = numOfCatagories;
        self.catagoryNumbers = np.zeros(numOfCatagories);
        self.average = [];

        # "private" variables
        self._catagoryLabels = catagoryLabels;
        self._imagePath = "";

    def updateData(self, imagePath, catagoryLabels):
        # Check if files have already been loaded
        if (imagePath != self._imagePath):
            self._imagePath = imagePath;
            self.fullData = self.__readImages(imagePath);
            self.average = self.__findAverageImg(self.fullData);

    # assures random placing of images
    def shuffleData(self):
        random.shuffle(self.fullData);

    # Data raw data is stored by class in a way that allows openCV manipulation
    # and easy shuffling of data. Therefore some legwork must be done to make it keras friendly
    def genMachineLearningData(self, shape):
        # Format raw data in keras friendly manner
        imageList = self.__getImages(shape);
        catagoryList = self.__getCatagories();
        # Split data into training, testing and validation data
        self.x_train, self.x_val, self.y_train, self.y_val = train_test_split(imageList, catagoryList, random_state = 0);
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x_train, self.y_train, random_state = 0);
        # Calculate weights of each of these datasets
        self.trainingDataWeights, self.trainingCatagoryCounts = self.__calculateWeights(self.y_train);
        self.validationDataWeights,  self.validationCatagoryCounts= self.__calculateWeights(self.y_val);
        self.testingDataWeights, self.testingCatagoryCounts = self.__calculateWeights(self.y_test);

    ############################# Private functions ############################
    # Keep in openCV format for as long as possible, more operations can be
    # performed in opnCV format
    def __readImages(self, path):
        print(path)
        print("loading data from: " + path);

        data = [];

        for imageFile in tqdm(os.listdir(path)):
            keys = self._catagoryLabels.keys();
            for i in range(0, len(keys)):
                if (imageFile.find(keys[i]) != -1):
                    label = self._catagoryLabels[keys[i]];
                    data.append([self.__imread(imageFile, path), label]);
                    self.datapoints += 1;
                    self.catagoryNumbers[int(label)] += 1;

        #self.weights = self.__setWeights();
        data = np.asarray(data);
        return data;

    def __imread(self, image, imagePath):
        includeSides = 1;
        path = os.path.join(imagePath,image)  # create path image
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE);
        return image;

    # returns list of images
    def __getImages(self, shape):
        images = [];
        print self.fullData.shape[0]
        for i in range(0, self.fullData.shape[0]):
            # allow reshaping of images, large images are expensive for machine learning
            # Subtract average, average is systematic noise from sensor
            im = cv2.resize(np.subtract(self.fullData[i][0], self.average), shape);
            im = np.asarray(im) # return as array for use in keras
            im = im.astype('float32') / 255; # Normalize between 0 and 1
            images.append(im);

        images = np.asarray(images);
        images = images[..., np.newaxis]; # add dimention so keras can read
        return images;

    # returns the categoris in an encoded form for use in keras
    def __getCatagories(self):
        catagories = [];
        for i in range(0, len(self.fullData)):
            catagories.append(self.fullData[i][1]);

        return self.__encodeData(catagories);

    # calculates weights of dataset before it has been hot encoded
    # takes in hot encoded list of catagories, calculates the number and ratio
    # of each
    def __calculateWeights(self, data):
        weights = {};
        catagoryCounts = np.zeros(data.shape[1]);

        # Counts number of each catagory
        for i in range(data.shape[0]):
            catagoryCounts = np.add(catagoryCounts, data[i]);

        for i in range(0, len(catagoryCounts)):
            weights[i] = float(catagoryCounts[i]/data.shape[0]);

        return weights, catagoryCounts

    # data must be encoded for use with keras
    def __encodeData(self, classifications):
        classifications = pd.DataFrame(classifications, columns = ["Type"]);
        encoder = OneHotEncoder(sparse = False);
        classifications = encoder.fit_transform(classifications);
        return classifications

    # Calculate the average image in the dataset
    def __findAverageImg(self, data):
        sumImg = np.zeros(data[0][0].shape, dtype = np.double);
        numOfImages = data.shape[0]
        for i in range(0, numOfImages):
            sumImg = sumImg + data[i][0];
        sumImg = sumImg/numOfImages
        return sumImg;

if __name__ == '__main__':
    # Label depending on the name of the image
    # Current nameing strucure is;
    #       HV = Healthy voulenteer
    #       PA & PT = scleroderma patient
    dataStore = dataHandler(2, {'HV':'0', 'PA':'1', 'PT':'1'});
    dataStore.updateData('/home/alex/Documents/dataset/mipDataBest', {'HV':'0', 'PA':'1', 'PT':'1'});
    dataStore.genMachineLearningData((64, 64))
    print dataStore.fullData[0][0].shape;
    dataStore.updateData('/home/alex/Documents/dataset/mipDataBest', {'HV':'0', 'PA':'1', 'PT':'1'});
    dataStore.updateData('/home/alex/Documents/dataset/mipDataRaw', {'HV':'0', 'PA':'1', 'PT':'1'});
