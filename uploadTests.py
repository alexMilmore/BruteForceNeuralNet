import genArchitecture as genModel
import databaseConnect as dbConnect
import numpy as np
import architectureTranslate as archTran

## Model settings
# This defines the type of model tested;
#       Each entry is of the form [layerType, constants, activaionFunction]
#       Any blank entry uses all possible default combinations
#       Inputing a list rather than a string causes the network to cycle through
#           the possible combinations with the list
# NOTE; if you're inputing images, make sure 1st layer is conv2D. I didn't
# accout for 1st layer being dense when I made this thing
#modelConstraints = [['conv2D', '', 'relu'], ['conv2D', '', 'relu'], ['dense', ['128', '64', '32', '16', '8'], 'relu'], ['dense', '2', ['sigmoid', 'tanh']]];
modelConstraints = [['conv2D', '8', 'tanh'], ['conv2D', ['4', '8'], 'relu'], ['dense', '128', 'relu'], ['dense', '2', 'sigmoid']];

# Any fields left blank in model constraints will cycle between the default
# values specified here
possibleLayers = ['conv2D', 'dense'];
possibleActivationFuntions = ['tanh', 'relu', 'sigmoid'];
possibleConstants = ['4', '8', '16', '32'];

### Training Hyperparameters
dataSize = 64;
numberOfImages = 100000000;
epochs = 20;
batchSize = 64;


######################## Actual code ############################################
# Create database cursor
cursor = dbConnect.dbCursor();

# generate the architecture of all possible models
testModels = genModel.genArchitecture(modelConstraints, [possibleLayers, possibleConstants, possibleActivationFuntions]);

# Upload test models to the server
# TODO ALLOW SPECIFYING DATASET NAME
print("Loading models to MySQL server");
count = cursor.findMaxID();
print count;

for entry in testModels:
    entryArray = np.asarray(entry);
    entryTxt = archTran.architectureToText(entryArray);
    cursor.inputIDKeyToServer(count, entryTxt, 'MIP', dataSize, epochs, batchSize);
    count += 1;
