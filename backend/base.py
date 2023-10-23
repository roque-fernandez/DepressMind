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


outputLocation = r"./outputs/"
uploadLocation = r"./upload/"

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
            print("Stored results intensity")
            
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

@app.route('/login', methods=['GET'])
def login():
    args = request.args
    username = args.get('username')
    password = args.get('password')
    
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

@app.route('/change-password', methods=['PUT'])   
def changePassword():
    username = json.loads(request.data)['username']
    oldPassword = json.loads(request.data)['oldPassword']
    newPassword1 = json.loads(request.data)['newPassword1']
    newPassword2 = json.loads(request.data)['newPassword2']

    if newPassword1 != newPassword2:
        return "Passwords do not match", 400

    currentUser = users.find_one({'username': username})
    print("User: ", currentUser['username'])
    if currentUser:
        # Check if the old password is correct
        if bcrypt.checkpw(oldPassword.encode('utf-8'), currentUser['password']):
            # Generate the hash of the new password
            newHashedPassword = bcrypt.hashpw(newPassword1.encode('utf-8'), bcrypt.gensalt())
            # Update the user's password in the database
            users.update_one({'username': username}, {'$set': {'password': newHashedPassword}})
            return "Password updated successfully", 200
        else:
            return "Wrong password", 400
    else:
        return "User not found", 404