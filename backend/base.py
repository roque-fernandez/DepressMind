from flask import Flask, request, jsonify, json, send_file
import os
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import json
import reddit as rd
import twitter as tw
import bcrypt
import fileStatistics as fst
import analyzer 

outputLocation = r"C:\Users\roque\OneDrive\Escritorio\TFG\react-login-signup-ui\backend\outputs\\"
uploadLocation = r".\upload\\"

app = Flask(__name__)

mongodb_client = MongoClient("mongodb://localhost:27017/")
db = mongodb_client['TFG']
users = db['users']
presence_results = db['presence_results']
stored_results = db['results']
intensity_results = db['intensity_results']

@app.route('/reddit', methods=['GET'])
def reddit():
    args = request.args
    searchType = args.get('type')

    if searchType == 'Generalist':
        outputName = rd.generalistCrawl(args)

    elif searchType == 'Subreddit':
        outputName = rd.subredditCrawl(args)

    elif searchType == 'User':
        outputName = rd.userCrawl(args)

    elif searchType == 'Keyword':
        outputName = rd.keywordCrawl(args)

    else:
        return "Bad request", 400

    route = outputLocation + outputName
    try:
        total,avgVotes,totalUsers = fst.redditStatistics(outputName)
        statistics = {
            "total": total,
            "avgVotes": avgVotes,
            "totalUsers": totalUsers
        }
        response = send_file(route)
        return response,200,{"statistics": statistics}
    except Exception as e:
        return str(e)

@app.route('/twitter', methods=['GET'])
def twitter():
    args = request.args
    outputName = tw.twitterCrawler(args)
    route = outputLocation + outputName
    try:
        total,avgLikes,avgRts,totalUsers = fst.twitterStatistics(outputName)
        statistics = {
            "total": total,
            "avgLikes": avgLikes,
            "avgRts": avgRts,
            "totalUsers": totalUsers
        }
        response = send_file(route)
        print(statistics)
        return response,200,{"statistics": statistics}
    except Exception as e:
        return str(e)

@app.route('/analysis', methods=['POST'])
def analysis():
    try:
        mode = request.args.get('mode')
        source = request.args.get('source')
        print("Mode and source: ",mode,source)
        f = request.files['file']
        f.save(os.path.join(uploadLocation, secure_filename(f.filename)))
        #if we already analysed a file of a user we return the stored results
        fileResults = stored_results.find_one({'username': 'pepe', 'filename': f.filename, 'mode':mode})
        
        if fileResults:
            resultsDict = json.loads(fileResults['results'])
            results = jsonify(resultsDict['analysis'],resultsDict['dailyAnalysis'],resultsDict['weeklyAnalysis'],resultsDict['monthlyAnalysis'])
            print("Stored results: ", fileResults['results'])
            print("Results dict:", resultsDict)
            print("Analysis: ",resultsDict['analysis'])
            return jsonify(resultsDict['analysis'],resultsDict['dailyAnalysis'],resultsDict['weeklyAnalysis'],resultsDict['monthlyAnalysis'])
        #if we didnt analysed this file yet we analyse it
        else:
            analysis = analyzer.analyzer(f.filename,mode=mode,source=source)
            dailyAnalysis,weeklyAnalysis,monthlyAnalysis = analyzer.timeAnalyzer(f.filename,mode=mode,source=source)
            resultsDict = {'analysis':analysis,'dailyAnalysis': dailyAnalysis, 'weeklyAnalysis': weeklyAnalysis, 'monthlyAnalysis':monthlyAnalysis}
            results = jsonify(analysis,dailyAnalysis,weeklyAnalysis,monthlyAnalysis)
            print(type(results))
            print("Results: ",json.dumps(resultsDict))
            #write results to mongo
            stored_results.insert_one({'username': 'pepe', 'filename': f.filename, 'mode':mode, 'results': json.dumps(resultsDict)})
            return jsonify(analysis,dailyAnalysis,weeklyAnalysis,monthlyAnalysis)
    except Exception as e:
        return str(e)

@app.route('/login', methods=['POST'])
def login():
    username = json.loads(request.data)['username']
    password = json.loads(request.data)['password']
    
    currentUser = users.find_one({'username':username})
    print("User: ",currentUser['username'])
    if currentUser:
        if bcrypt.checkpw(password.encode('utf-8'), currentUser['password']):
            return "Ok",200
        else:
            return "Wrong password",400
    else:
        return "User does not exist",404

@app.route('/register', methods=['POST'])
def register():
    username = json.loads(request.data)['username']
    password = json.loads(request.data)['password']
    print("User: ",username)
    if not username:
        return 'Missing username',400
    if not password:
        return 'Missing password',400
    #check if already exists
    if users.find_one({'username':username}):
        return 'Already existing user',400
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    #insert into db
    users.insert_one({'username': username, 'password': hashedPassword})
    return "Ok",200

@app.route('/test', methods=['POST'])   
def test():
    l = [1,2,3,'hola']
    return jsonify(l) 