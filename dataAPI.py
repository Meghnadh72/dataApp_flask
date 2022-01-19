import os
from flask import Flask
from flask import request, jsonify, make_response
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData
from flask_cors import CORS
from sqlalchemy.sql.expression import text


app = Flask(__name__)


cors = CORS(app, resources={r"/*": {"origins": "*"}})
# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

#GLOBAL VARIABLES
connectionString = 'postgresql://sampledbuser:sample@localhost:5432/sample'

#Engine created at module level
dbEngine = create_engine(connectionString)


def createTablewithHeadersList(headersList,datasetName):
    #Create Query using String 
    createQuery = "Create Table " + datasetName +" ( "
    for eachHeader in range(len(headersList) - 1):
        createQuery = createQuery + headersList[eachHeader] + " VARCHAR  (255) ,"
    createQuery = createQuery + headersList[eachHeader + 1] + " VARCHAR (255) );"
    dbconn = getDatabaseConnection()
    curs = dbconn.cursor()
    curs.execute(createQuery)
    dbconn.commit()
    curs.close()
    dbconn.close()
    print("CREATED TABLE " + datasetName + " ---------------------")


def insertDatasetName(datasetName):
    insertDatasetQuery = "INSERT INTO datasetlist (datasetname) values('" + datasetName + "');"
    dbconn = getDatabaseConnection()
    curs = dbconn.cursor()
    try:
        curs.execute(insertDatasetQuery)
    except psycopg2.errors.UniqueViolation:
        pass
    dbconn.commit()
    curs.close()
    dbconn.close()


    

@app.route("/datasets", methods=['GET'])
def getOrPostitems():
    datasetList = []
    if request.method == 'GET':
        with dbEngine.connect() as dbConn:
            datasetListResults = dbConn.execute("SELECT *FROM datasetlist")
        datasetListResults = list(datasetListResults)
        for eachdataset in datasetListResults:
            datasetList.append(list(eachdataset)[0])

        resp  = make_response({"datasetList" : datasetList} )
        resp.headers["Content-Type"] = "application/json"
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    	
def getDatabaseConnection():
    conn = None
    try:
        conn = psycopg2.connect(
    	host="localhost",
    	database="sample",
    	user="sampledbuser",
    	password="sample")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn

# Get the uploaded files
@app.route("/datasets", methods=['POST'])
#@cross_origin()
def uploadFiles():
      print("INto the uploadFile API")
      print("datasetName " + str(request.form.get("datasetName")))

      # get the uploaded file
      uploaded_file = request.files["csvfile"]
      print(type(uploaded_file))
      dataframeCsv = pd.read_csv(uploaded_file)
      headersList = list(dataframeCsv.columns)
      print("HeaderList : " )
      print(headersList)
      datasetName = str(request.form.get("datasetName"))
      print("DatasetName " + datasetName) 
      insertDatasetName(datasetName)
      #HERE A Better way to do is to use create engine and ORM model in SQL ALCHEMY to create Table.
      #createTablewithHeadersList(headersList,datasetName)
      #SAVE CSV FILE INTO CREATED TABLE
      connectionString = 'postgresql://sampledbuser:sample@localhost:5432/sample'
      dataframeCsv.to_sql(datasetName, con=dbEngine, if_exists = 'append', index=False)
      
      #dataframeCsv.to_sql('test', engine, index = False)
      print("done")
      return "Meghnadh"


@app.route("/plotGraph", methods = ["GET"])
def plotGraph():
    firstCol25 = []
    secondCol25 = []
    datasetName = request.args.get("dsName")
    firstCol = request.args.get("firstCol")
    secondCol = request.args.get("secondCol")
    connectionString = 'postgresql://sampledbuser:sample@localhost:5432/sample'
    selectQuery = "SELECT " + str(firstCol) + ", " + str(secondCol) + " FROM " + str(datasetName) + " limit 25;"
    selectQuery = text(selectQuery)
    with dbEngine.connect() as dbConn:
            datasetResults = dbConn.execute(selectQuery)
    datasetResults = list(datasetResults)
    
    #breakpoint()
    #Process the results - Original Format : [(level, value ), (level,value) .... ]
    for eachdataset in datasetResults:
        firstCol25.append(list(eachdataset)[0])
        secondCol25.append(list(eachdataset)[1])
    plotResponse = make_response({"Col1" : firstCol25, "Col2" : secondCol25 })
    plotResponse.headers['Access-Control-Allow-Origin'] = '*'
    return plotResponse
    

@app.route("/getHeadersList", methods = ["GET"])
def getHeadersList():
    headersList  = []
    datasetName  = request.args.get("datasetName")
    colQuery     = "SELECT * FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '" + str(datasetName) +"';"
    columnsQuery = text(colQuery)

    with dbEngine.connect() as dbConn:
        results = dbConn.execute(columnsQuery)
    
    headerListresults = list(results)
    for eachResult in headerListresults:
        headersList.append(list(eachResult)[3])
    responseh = make_response({"headersList" : headersList})
    return responseh


@app.route("/compute", methods = ["GET"])
def computeValue():
    datasetName = request.args.get("datasetName")
    computeFlag = request.args.get("value")
    column      = request.args.get("column")
    q           = "SELECT " + str(column) + " FROM " + datasetName + ";"
    selectQuery = text(q)

    with dbEngine.connect() as dbConn:
        res = dbConn.execute(selectQuery)

    colAsDataframe = pd.DataFrame(res.scalars().all())

    if int(computeFlag) == 0:
        returnValue = colAsDataframe.min()
        return make_response({"value" : str(returnValue[0])})
    else:
        returnValue = colAsDataframe.max()
        return make_response({"value" : str(returnValue[0])})



 
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)




