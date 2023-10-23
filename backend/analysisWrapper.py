#FILE USED WHEN COMPUTING IN GPU TO STORE RESULTS IN A JSON
import json
import analyzer 

outputLocation = r"./outputs/"
uploadLocation = r"./upload/"


def analysis(file):
    try:
        analysis, intenseSentences = analyzer.analyzer(file, mode='intensity')
        dailyAnalysis, weeklyAnalysis, monthlyAnalysis = analyzer.timeAnalyzer(file, mode='intensity')
        resultsDict = {'analysis': analysis, 'dailyAnalysis': dailyAnalysis, 'weeklyAnalysis': weeklyAnalysis, 'monthlyAnalysis': monthlyAnalysis, 'intenseSentences': intenseSentences}

        with open('results.json', 'w') as f:
            json.dump(resultsDict, f)

        print("*******************************")
        print("RESULTS STORED IN results.json")
    except Exception as e:
        return str(e)

analysis("demo_analyzer_short_v3.json")

