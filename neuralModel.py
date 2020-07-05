from keras.layers import Input, Dense, Conv2D, Reshape, Flatten, MaxPooling2D, UpSampling2D
from keras.models import Model, Sequential
from sklearn.model_selection import train_test_split
import importData as ipd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class neuralModel:
    def __init__(self, architecture, inputHandler):
        # String specifying the architecture of the network
        self.architectureString = self.genName(architecture);
        # Make model
        self.model = Sequential();
        self.layerCount = 0;
        for i in range(0, len(architecture)):
            self.layerCount += self.layerFunction(self.model, architecture[i][0], int(architecture[i][1]), architecture[i][2]);
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics = ['accuracy'])
        self.inputHandler = inputHandler;

        # prediction flag to prevent multiple predictions on the same data
        self.prediction = False;

    def genName(self, architecture):
        name = '';
        for layer in architecture:
            layerString = '_'.join(layer);
            name += layerString + '__';
        return name

    ### Different layer functions. These were designed to make a standard method
    # for creating layers from an array of settings
    def layerFunction(self, model, type, constant, activation):
        layerCount = 0;
        if (type == 'convSqueeze'):
            layerCount = self.convSqueezeLayer(model, constant, activation);
            return layerCount;
        elif (type == 'convExpand'):
            layerCount = self.convExpandLayer(model, constant, activation);
            return layerCount;
        elif (type == 'convFlatten'):
            layerCount = self.convFlatLayer(model, activation);
            return layerCount;
        elif (type == 'conv2D'):
            layerCount = self.conv2DLayers(model, [constant], [activation]);
            return layerCount;
        elif (type == 'dense'):
            layerCount = self.denseLayers(model, [constant], [activation]);
            return layerCount;
        elif (type == 'denseTo2D'):
            layerCount = self.denseTo2DLayer(model, constant, activation);
            return layerCount;
        else:
            print("Unrecognised layer type in autoencoder model, cannot process");

    ####### Functions for building neural networks
    # applies a convolution and a pooling layer
    def convSqueezeLayer(self, model, convSize, activaionFunction):
        model.add(Conv2D(convSize, kernel_size=(3,3), activation=activaionFunction, padding='same'));
        model.add(MaxPooling2D((2,2)));
        return 2;

    # applies multiple convolution and pooling layers
    def convSqueezeLayers(self, model, convLayers, activaionFunction):
        counter = 0;
        for i in range(0, len(convLayers)):
            counter += self.convSqueezeLayer(model, convLayers[i], activaionFunction[i]);
        return counter;

    # applies a convolution and outputs 1d rather than 2d data
    def convFlatLayer(self, model, activaionFunction):
        model.add(Conv2D(1, kernel_size=(3,3), activation=activaionFunction, padding='same'));
        model.add(Flatten());
        return 2;

    def convExpandLayer(self, model, convSize, activaionFunction):
        model.add(Conv2D(convSize, kernel_size=(3,3), activation=activaionFunction, padding='same'));
        model.add(UpSampling2D((2, 2)));
        return 2;

    def convExpandLayers(self, model, convLayers, activaionFunction):
        counter = 0;
        for i in range(0, len(convLayers)):
            counter += self.convExpandLayer(model, convLayers[i], activaionFunction[i]);
        return counter;

    def denseTo2DLayer(self, model, sideLength, activationFunction):
        model.add(Dense((sideLength)*(sideLength), activation=activationFunction));
        model.add(Reshape((sideLength, sideLength, 1)));
        return 2;

    def denseLayers(self, model, sizes, activationFunctions):
        counter = 0;
        for i in range(0, len(sizes)):
            model.add(Dense(sizes[i], activation=activationFunctions[i]));
            counter += 1;
        return counter;

    def conv2DLayers(self, model, sizes, activationFunctions):
        counter = 0;
        for i in range(0, len(sizes)):
            model.add(Conv2D(sizes[i], kernel_size=(3,3), activation=activationFunctions[i], padding = 'same'));
            counter += 1;
        return counter;

    def train(self, numOfEpochs, batchSize):
        self.history = self.model.fit(self.inputHandler.x_train, self.inputHandler.y_train, \
        epochs=numOfEpochs, batch_size= batchSize, shuffle=True, \
        validation_data=(self.inputHandler.x_val, self.inputHandler.y_val));

    def saveModel(self, saveName):
        self.model.save(saveName + ".h5");

    def getTrainingData(self):
        return self.history.history;

    # predicting multiple times wastes computation, so its best to check if
    # predictions have already been made
    # TODO; Allow model to predict over multiple sets of training data
    def predict(self):
        if (self.prediction == False):
            self.predictions = self.model.predict(self.inputHandler.x_test);
            self.prediction = True;

    # get the loss and validation loss of the model
    def getMetrics(self):
        # Collect all metrics
        metrics = {'architecture' : self.architectureString, \
        'loss' : self.history.history['loss'][-1], \
        'val_loss' : self.history.history['val_loss'][-1], \
        'accuracy' : self.history.history['accuracy'][-1]}
        return metrics;

    def summary(self):
        self.model.summary();

class classifier(neuralModel):
    def __init__(self, architecture, inputHandler):
        neuralModel.__init__(self, architecture, inputHandler);

    def getTestingData(self):
        self.predict();
        return {'predictions' : self.predictions, 'answers' : self.inputHandler.y_test};

    # Predicts using testing data and returns a dictionary with the percentage
    # of correct predictions overall and in each catagory
    def classificationAccuracy(self):
        self.predict();
        totalTests = self.predictions.shape[0];
        numOfClassifications = self.predictions.shape[1];
        correctPredictions = 0;
        accuracyList = [0] * numOfClassifications;

        # Count the total number correct in each catagory
        for i in range(0, totalTests):
            if (np.argmax(self.predictions[i]) == np.argmax(self.inputHandler.y_test[i])):
                    accuracyList[np.argmax(self.predictions[i])] += 1;
                    correctPredictions += 1;

        # Create output dictionary
        metrics = {'totalAccuracy' : float(correctPredictions)/totalTests}
        for i in range (0, numOfClassifications):
            print "current Acc"
            print accuracyList[i]
            print self.inputHandler.testingCatagoryCounts[i];
            print accuracyList[i]/self.inputHandler.testingCatagoryCounts[i];
            metrics['class' + str(i + 1) + 'Accuracy'] = accuracyList[i]/self.inputHandler.testingCatagoryCounts[i];

        print ("testingCats");
        print metrics;

        return metrics;

    # Fuses together the model metrics from the parent neuralModel class and
    # adds the classification accuracy from this class
    def overviewMetrics(self):
        basicMetrics = self.getMetrics();
        accuracyMetrics = self.classificationAccuracy();
        fullMetrics = basicMetrics.copy();
        fullMetrics.update(accuracyMetrics);
        return fullMetrics;

    def train(self, numOfEpochs, batchSize):
        self.history = self.model.fit(self.inputHandler.x_train, self.inputHandler.y_train, \
        epochs=numOfEpochs, batch_size= batchSize, shuffle=True, \
        validation_data=(self.inputHandler.x_val, self.inputHandler.y_val), \
        class_weight = self.inputHandler.testingDataWeights);

# TODO work in progress
class encoderDecoder(neuralModel):
    def __init__(self, inputShape, encodedShape, encoderArchitecture, decoderArchitecture):

        # Make the encoder and decoder
        self.encoder = neuralModel(inputShape, encoderArchitecture)
        self.decoder = neuralModel(encodedShape, decoderArchitecture)

        self.architectureString = self.genName(encoderArchitecture + decoderArchitecture);

        # Create seperate full encoderDecoder model from encoder and decoder
        encoderDecoderInput = Input(shape = inputShape);
        x = self.encoder.model(encoderDecoderInput);
        encoderDecoderOutput = self.decoder.model(x)
        self.model = Model(encoderDecoderInput, encoderDecoderOutput);
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics = ['accuracy'])

        self.dataSize = inputShape[0]

    def displayGeneration(self, saveName):
        encoded_imgs = self.encoder.model.predict(self.inputHandler.x_test);
        decoded_imgs = self.decoder.model.predict(encoded_imgs);

        n = 5;  # how many digits we will display
        plt.figure(figsize=(20, 5));
        for i in range(n):
            # display original
            ax = plt.subplot(2, n, i + 1);
            plt.imshow(self.inputHandler.x_test[i].reshape((self.dataSize, self.dataSize)));
            plt.gray();
            ax.get_xaxis().set_visible(False);
            ax.get_yaxis().set_visible(False);

            # display reconstruction
            ax = plt.subplot(2, n, i + 1 + n);
            plt.imshow(decoded_imgs[i].reshape((self.dataSize, self.dataSize)));
            plt.gray();
            ax.get_xaxis().set_visible(False);
            ax.get_yaxis().set_visible(False);
        plt.savefig(saveName);
        plt.clf();
