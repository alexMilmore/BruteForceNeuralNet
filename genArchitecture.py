import copy

# produce all possible combinations of the possibilities vactor for one layer
def listPossibleLayers(constraints, possibilities):
    dimentions = len(possibilities);
    possibleLayers = [];
    for i in range(0, dimentions):
        # check if there is a constraint
        if (isinstance(constraints[i],list)):
            possibleLayers = layerOfPossibility(possibleLayers, constraints[i]);
        elif (constraints[i] == ''):
            possibleLayers = layerOfPossibility(possibleLayers, possibilities[i]);
        # just list every possibility
        else:
            possibleLayers = addToLayer(possibleLayers, constraints[i]);

    return possibleLayers;

def addToLayer(layer, addition):
    layerList = [];

    if (len(layer) == 0):
        layerList.append([addition]);
    else:
        for object in layer:
                val = copy.deepcopy(addition)
                objVal = copy.deepcopy(object)
                layerList.append(objVal + [val]);
    return layerList;

def layerOfPossibility(input, possibilities):
    layerList = [];

    if (len(input) == 0):
        for item in possibilities:
            val = copy.deepcopy(item);
            layerList.append([val]);
    else:
        for object in input:
            for item in possibilities:
                val = copy.deepcopy(item);
                objVal = copy.deepcopy(object);
                layerList.append(objVal + [val]);
    return layerList;

def addLayer(previousLayer, addition):
    newLayer = [];
    if (len(previousLayer) == 0):
        for item in addition:
            val = copy.deepcopy(item)
            newLayer.append([val]);
    else:
        for i in range(0, len(previousLayer)):
            for item in addition:
                val = copy.deepcopy(item);
                objVal = copy.deepcopy(previousLayer[i]);
                newLayer.append(objVal + [val]);

    return newLayer

def makeLayersFit(architecture):
    for i in range(0, len(architecture)):
            for j in range(0, len(architecture[i]) - 1):
                currentLayer = architecture[i][j][0];
                nextLayer = architecture[i][j+1][0];



                if currentLayer != nextLayer:

                    if (currentLayer == 'dense') and (nextLayer == 'conv2D'):
                        architecture[i][j][0] = "denseTo2D";
                    elif (currentLayer == 'conv2D') and (nextLayer == 'dense'):
                        architecture[i][j][0] = 'convFlatten';

    return architecture;

def genArchitecture(constraints, possibilities):
    val = [];
    layers = len(constraints);

    for i in range(0, layers):
        possibleAdditions = listPossibleLayers(constraints[i], possibilities);
        val = addLayer(val, possibleAdditions);
    val = makeLayersFit(val)

    return val;

if __name__ == "__main__":
    test = genArchitecture([['a','',''],['','','y'],['','','y']], [['conv2D', 'dense'], ['8'], ['relu']])
    print testz;
