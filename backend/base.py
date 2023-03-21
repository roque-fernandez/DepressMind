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


outputLocation = r".\outputs\\"
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
    print("Route:",route)
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
        username = request.args.get('username')
         
        print("Mode, source and username: ",mode,source,username)
        f = request.files['file']
        f.save(os.path.join(uploadLocation, secure_filename(f.filename)))

        if mode == 'presence':
            #if we already analysed a file of a user we return the stored results
            fileResults = stored_results.find_one({'username': username, 'filename': f.filename, 'mode':mode})
            
            if fileResults:
                resultsDict = json.loads(fileResults['results'])
                return jsonify(resultsDict['analysis'],resultsDict['dailyAnalysis'],resultsDict['weeklyAnalysis'],resultsDict['monthlyAnalysis'])
            #if we didnt analysed this file yet we analyse it
            else:
                print("PRESENCE: FILE NOT STORED")
                analysis= analyzer.analyzer(f.filename,mode=mode,source=source)
                dailyAnalysis,weeklyAnalysis,monthlyAnalysis = analyzer.timeAnalyzer(f.filename,mode=mode,source=source)
                resultsDict = {'analysis':analysis,'dailyAnalysis': dailyAnalysis, 'weeklyAnalysis': weeklyAnalysis, 'monthlyAnalysis':monthlyAnalysis}
                #print("Results: ",json.dumps(resultsDict))
                #write results to mongo
                stored_results.insert_one({'username': username, 'filename': f.filename, 'mode':mode, 'results': json.dumps(resultsDict)})
                return jsonify(analysis,dailyAnalysis,weeklyAnalysis,monthlyAnalysis)
        #INTENSITY
        else:
            #if we already analysed a file of a user we return the stored results
            fileResults = stored_results.find_one({'username': username, 'filename': f.filename, 'mode':mode})
            
            if fileResults:
                resultsDict = json.loads(fileResults['results'])
                return jsonify(resultsDict['analysis'],resultsDict['dailyAnalysis'],resultsDict['weeklyAnalysis'],resultsDict['monthlyAnalysis'],resultsDict['intenseSentences'])
            #if we didnt analysed this file yet we analyse it
            else:
                analysis,intenseSentences = analyzer.analyzer(f.filename,mode=mode,source=source)
                dailyAnalysis,weeklyAnalysis,monthlyAnalysis = analyzer.timeAnalyzer(f.filename,mode=mode,source=source)
                resultsDict = {'analysis':analysis,'dailyAnalysis': dailyAnalysis, 'weeklyAnalysis': weeklyAnalysis, 'monthlyAnalysis':monthlyAnalysis,'intenseSentences':intenseSentences}
                print("Results: ",json.dumps(resultsDict))
                #write results to mongo
                stored_results.insert_one({'username': username, 'filename': f.filename, 'mode':mode, 'results': json.dumps(resultsDict)})
                return jsonify(analysis,dailyAnalysis,weeklyAnalysis,monthlyAnalysis,intenseSentences)

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