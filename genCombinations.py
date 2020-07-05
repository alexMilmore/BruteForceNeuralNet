def generateCombinations(possibilities, length):
    startList = [];
    list = [];

    if (len(list) == 0):
        startList = possibilities;

    for i in range(0, length - 1):
        list = [];
        for part in startList:
            for item in possibilities:
                list.append(part + item);
        startList = list;
    return list;
