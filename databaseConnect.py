import pymysql.cursors
import getpass
import logging

class dbCursor():

    def __init__(self):
        # Connect to the database
        print("Database server host");
        self.hostName = raw_input();
        print("Username for database");
        self.userName = raw_input();
        print("Input name of database");
        self.databaseName = raw_input();
        print("Database password");
        self.DBpassword = getpass.getpass();
        self.conn = pymysql.connect(host=self.hostName,
                                     user=self.userName,
                                     password=self.DBpassword,
                                     db=self.databaseName,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor();
        # create log file
        self.logger = logging.getLogger('dbConnectLog')
        logging.basicConfig(filename='error.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    ########################## Insert data into database ###########################
    def inputIDKeyToServer(self, testID, modelArchitecture, dataSet, imageDimentions, epochs, batchSize):
        try:
            sqlCommand = 'INSERT INTO IDKey ( \
            testID, \
            modelArchitecture, \
            dataSet, \
            imageDimentions, \
            epochs, \
            batchSize, \
            tested, \
            error) \
            VALUES (%s, %s, %s, %s, %s, %s, false, false);' % \
            (testID , \
            '\'' + modelArchitecture +  '\'', \
            '\'' + dataSet +  '\'', \
            imageDimentions, \
            epochs,
            batchSize);

            self.cursor.execute(sqlCommand);
            self.conn.commit();
        except:
            print("Failed to update the server, check logs");
            self.logError("Error in command", sqlCommand);

    # Adds data to the overview table in the MySQL server
    def inputOverviewToServer(self, testID, loss, predictionAccuracy, healthyPredictionAccuracy, sickPredictionAccuracy):
        try:
            sqlCommand = 'INSERT INTO overview ( \
              testID, \
              loss, \
              predictionAccuracy, \
              healthyPredictionAccuracy, \
              sickPredictionAccuracy) \
            VALUES (%s, %s, %s, %s, %s);' % \
                (testID, \
                loss, \
                predictionAccuracy, \
                healthyPredictionAccuracy, \
                sickPredictionAccuracy);

            self.cursor.execute(sqlCommand);
            self.conn.commit();
        except:
            print("Failed to update the server, check logs");
            self.logError("Error in command", sqlCommand);

    # Adds data to the training data table in the MySQL server
    def inputTrainDataToServer(self, testID, fold, epoch, loss):
        try:
            sqlCommand = 'INSERT INTO trainingLogs ( \
              testID, \
              fold, \
              epoch, \
              loss) \
            VALUES (%s, %s, %s, %s);' % \
                (testID, fold, epoch, loss);

            self.cursor.execute(sqlCommand);
            self.conn.commit();
        except:
            print("Failed to update the server, check logs");
            self.logError("Error in command", sqlCommand);

    # Adds data to the test data table in the MySQL server
    def inputTestDataToServer(self, testID, fold, modelOutput, correctAnswer):
        try:
            sqlCommand = "INSERT INTO testingLogs ( \
              testID, \
              fold, \
              modelOutput, \
              correctAnswer) \
            VALUES (%s, %s, %s, %s);" % \
                (testID, fold, '\'' + modelOutput + '\'', '\'' + correctAnswer + '\'');

            self.cursor.execute(sqlCommand);
            self.conn.commit();
        except:
            print("Failed to update the server, check logs");
            self.logError("Error in command", sqlCommand);

    ############################ Query from database ###############################
    def readTests(self):
        sqlCommand = 'SELECT * FROM IDKey WHERE tested = false;';
        self.cursor.execute(sqlCommand);
        result = self.cursor.fetchall();
        return result;

    def lookUpImagePath(self, dataSet):
        sqlCommand = 'SELECT filepath FROM inputData WHERE dataSet = \'%s\'' % (dataSet);
        self.cursor.execute(sqlCommand);
        result = self.cursor.fetchone();
        return result['filepath'];

    def findMaxID(self):
        sqlCommand = 'SELECT MAX(testID) from IDKey'
        self.cursor.execute(sqlCommand);
        result = self.cursor.fetchone();

        if (result['MAX(testID)'] == None):
            return 0;

        return result['MAX(testID)'] + 1;

    def logError(self, message, errorCmd):
        self.logger.warning(message);
        cmd = errorCmd.strip();
        self.logger.warning(cmd);

    ######################### Change values in database ########################
    def markCompleted(self, ID):
        sqlCommand = 'UPDATE IDKey SET tested = 1 WHERE testID = %s;' % (ID);
        self.cursor.execute(sqlCommand);
        self.conn.commit();

# unit testing
if __name__ == "__main__":
    cursorTest = dbCursor();
    cursorTest.inputOverviewToServer(20, 'a', 'b', 'c', 'd');
