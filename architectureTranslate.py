def architectureToText(array):
    text = ''

    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            text += array[i,j];
            text += ',';
        text += '_';
    return text;

# This is kinda gross, but gets the job done
def textToArchitecture(text):
    architecture = [];
    layer = ['', '', ''];
    index = 0;

    for i in range(0, len(text)):
        if (text[i] == ','):
            index += 1;
            if index > 3:
                index = 0;
        elif (text[i] == '_'):
            architecture.append(layer);
            layer = ['', '', ''];
            index = 0;
        else:
            layer[index] += text[i];

    return architecture;
