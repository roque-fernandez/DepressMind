from sentence_transformers import SentenceTransformer,util
import pickle
import torch
import json
import datetime
model = SentenceTransformer('all-MiniLM-L6-v2')
presenceFile = r".\BDI\bdi_presence.txt"
intensityFile = r".\BDI\bdi_intensity.txt"
outputLocation = r".\upload\\"
threshold = 0.35

#############################################################################################################  
# TIME ANALYSIS
############################################################################################################# 

def timeAnalyzer(file,source='reddit',mode='presence'):
    objectArray = jsonToObjectArray(file)
    #dictionary where key is time period and value is an array of texts
    months = groupByMonth(objectArray,source)
    weeks = groupByWeek(objectArray,source)
    days = groupByDay(objectArray,source)
    #dictionary where key is time period and value is an array with the results of the analysis
    monthlyAnalysis = {}
    weeklyAnalysis = {}
    dailyAnalysis = {}
    #get results for each time period
    for key in months:
        if mode == 'presence':
            results = sentencePresence(months[key])
        else:
            results = sentenceIntensity(months[key],threshold=threshold)
        monthlyAnalysis[str(key)] = results

    for key in weeks:
        if mode == 'presence':
            results = sentencePresence(weeks[key])
        else:
            results = sentenceIntensity(weeks[key],threshold=threshold)
        weeklyAnalysis[str(key)] = results

    for key in days:
        if mode == 'presence':
            results = sentencePresence(days[key])
        else:
            results = sentenceIntensity(days[key],threshold=threshold)
        dailyAnalysis[str(key)] = results

    # print("Monthly analysis")
    # print(monthlyAnalysis)
    # print("Weekly analysis")
    # print(weeklyAnalysis)
    # print("Daily analysis")
    # print(dailyAnalysis)

    return monthlyAnalysis,weeklyAnalysis,dailyAnalysis

def jsonToObjectArray(file):
    path = outputLocation + file
    objectArray = []
    with open(path, encoding="utf8") as f:
        content = f.read()
        decoder = json.JSONDecoder()
        while content:
            value, new_start = decoder.raw_decode(content)
            content = content[new_start:].strip()
            # Store it in a container and use it later:
            objectArray.append(value)

    #print(objectArray)
    return objectArray

def groupByWeek(objects,source):
    #set the type of text field
    textField = 'text'
    if source == 'twitter':
        textField = 'tweet'  
    groups = {}
    # Iterate through the objects and extract the date field
    for obj in objects:
        if source == 'reddit':
            dateStr = obj['date'].split('T')[0].strip()
        else:
            dateStr = obj['date']
        # Convert the date string to a datetime object
        date = datetime.datetime.strptime(dateStr, '%Y-%m-%d')
        # Get the year and week number for the date
        year, week, _ = date.isocalendar()
        # Add the text to the dictionary using the year and week number as the key
        if (year, week) not in groups:
            groups[(year, week)] = []
        splittedTextField = obj[textField].split('.')
        for t in splittedTextField:
            groups[(year, week)].append(t)
    return groups

def groupByMonth(objects,source):
    #set the type of text field
    textField = 'text'
    if source == 'twitter':
        textField = 'tweet'  
    groups = {}
    # Iterate through the objects and extract the date field
    for obj in objects:
        if source == 'reddit':
            dateStr = obj['date'].split('T')[0].strip()
        else:
            dateStr = obj['date']
        # Convert the date string to a datetime object
        date = datetime.datetime.strptime(dateStr, '%Y-%m-%d')
        # Get the year,month, day number for the date
        year = date.year
        month = date.month
        day = date.day
        # Add the text to the dictionary using the year and week number as the key
        if (year, month, day) not in groups:
            groups[(year, month, day)] = []
        groups[(year, month, day)].append(obj[textField])
    return groups

def groupByDay(objects,source):
    #set the type of text field
    textField = 'text'
    if source == 'twitter':
        textField = 'tweet'  
    groups = {}
    # Iterate through the objects and extract the date field
    for obj in objects:
        if source == 'reddit':
            dateStr = obj['date'].split('T')[0].strip()
        else:
            dateStr = obj['date']
        # Convert the date string to a datetime object
        date = datetime.datetime.strptime(dateStr, '%Y-%m-%d')
        # Get the year,month, day number for the date
        year = date.year
        month = date.month
        # Add the text to the dictionary using the year and week number as the key
        if (year, month) not in groups:
            groups[(year, month)] = []
        groups[(year, month)].append(obj[textField])
    return groups

#############################################################################################################  
# GENERAL
############################################################################################################# 

def analyzer(file,source='reddit',mode='presence'):
    texts = getTextFromJson(file,source=source)
    sentences = []
    for t in texts:
        splittedText = t.split('.')
        for st in splittedText:
            sentences.append(st)
    if mode == 'presence':
        result = sentencePresence(sentences)
    else:
        result = sentenceIntensity(sentences,threshold=threshold)
    #print(result)
    return result

def getTextFromJson(file,source='reddit'):
    path = outputLocation + file
    with open(path, encoding="utf8") as f:
        content = f.read()
        decoder = json.JSONDecoder()
        texts = []
        while content:
            value, new_start = decoder.raw_decode(content)
            content = content[new_start:].strip()
            # You can handle the value directly in this loop:
            if source == 'reddit':
                text = value['text']
            else: 
                text = value['tweet']
            # Or you can store it in a container and use it later:
            texts.append(text)
    return texts

def createEmbeddings(file,mode='presence'):
    #list of the embeddings for each question
    embeddings = []
    #list of every option of every question
    questions = []
    #points of every answer
    points = []
    #embeddings of the sentences of a question
    currentQuestion = []
    #points of the sentences of a question
    currentQuestionPoints = []
    #read BDI file
    with open(file) as f:
        lines = f.read().splitlines()
    
    for l in lines:
        if l != '#':
            if(mode=='presence'):
                currentQuestion.append(l)
            else:
                currentQuestionPoints.append(l.split("|")[0])
                currentQuestion.append(l.split("|")[1])
        else: 
            currentQuestionEmbeddings = model.encode(currentQuestion, convert_to_tensor=True)
            embeddings.append(currentQuestionEmbeddings)
            points.append(currentQuestionPoints)
            questions.append(currentQuestion)
            #print(currentQuestion)
            #print(currentQuestionPoints)
            #print(currentQuestionEmbeddings)
            #print('***********************************')
            currentQuestion = []
            currentQuestionPoints = []
    #print(embeddings)
    #print(points)
    if(mode=='presence'):
        return embeddings,questions
    else:
        return embeddings,points,questions

def printResult(res):
    for i,value in enumerate(res):
        if isinstance(value, float):
            value = round(value,3)
        print('Question',i+1, ':', value)

#############################################################################################################  
# PRESENCE
#############################################################################################################        

def sentencePresence(sentences,printFlag=False):
    prevalenceEmbeddings,questions = createEmbeddings(presenceFile)
    print("Questions")
    print(questions)
    print("PrevalenceEmbeddings")
    print(prevalenceEmbeddings)
    sentencesEmbedding = model.encode(sentences, convert_to_tensor=True)
    result = []
    questionIndex = 0
    for questionEmbeddings in prevalenceEmbeddings:
        #Compute cosine-similarities
        cosineScores = util.cos_sim(sentencesEmbedding, questionEmbeddings)
        #get the max similarity of every sentence within a question
        maxScores = [torch.max(l) for l in cosineScores]
        #get the average value of similarity of the sentences
        avgScore = sum(maxScores) / len(maxScores)
        result.append(avgScore)

        if printFlag:
            print('Question:',questionIndex+1)
            print('Scores:')
            for i in range(len(sentences)):
                for j in range(len(questions[questionIndex])):
                    if cosineScores[i][j] > 0.4:
                        print("{} \t\t {} \t\t Score: {:.4f}".format(sentences[i], questions[questionIndex][j], cosineScores[i][j]))
            print("Cosine scores:",cosineScores)
            print("Max scores:",maxScores)
            print("Avg score:",avgScore)
            print("****************************")

        questionIndex += 1
    #getting value of tensors and setting minimum value to 0
    result = [0 if t.item() < 0 else t.item() for t in result]
    printResult(result)
    #return result
    return result

#############################################################################################################  
# INTENSITY
############################################################################################################# 

def sentenceIntensity(sentences,printFlag=False,threshold=0.2):
    prevalenceEmbeddings,points,questions = createEmbeddings(intensityFile,mode='intensity')
    sentencesEmbedding = model.encode(sentences, convert_to_tensor=True)
    result = []
    questionIndex = 0
    for questionEmbeddings in prevalenceEmbeddings:
        
        #Compute cosine-similarities
        cosineScores = util.cos_sim(sentencesEmbedding, questionEmbeddings)
        #apply the threshold
        filteredScores = filterBelowThreshold(cosineScores, threshold)
        #get the index of the max similarity 
        maxSimilarityIndex,maxSimilarity = maxIndexOfScores(filteredScores)
        #get the points corresponding to that index
        maxPoints = int(points[questionIndex][maxSimilarityIndex])
        #append the max points
        result.append(maxPoints)
        
        if printFlag:
            print('Question:',questionIndex+1)
            print('Scores:')
            for i in range(len(sentences)):
                for j in range(len(questions[questionIndex])):
                    print("{} \t\t {} \t\t Score: {:.4f}".format(sentences[i], questions[questionIndex][j], cosineScores[i][j]))
            print("Cosine scores:",cosineScores)
            print("Max similarity:",maxSimilarity)
            print("Max similarity index:",maxSimilarityIndex)
            print("****************************")

        questionIndex += 1
    printResult(result)
    diagnosis(result)
    return result

def filterBelowThreshold(tensors, threshold):
    # Iterate over the list of lists of tensors
    for tensorList in tensors:
        # Iterate over the list of tensors
        for tensor in tensorList:
            # Filter the tensor values below the threshold
            tensor[tensor < threshold] = 0
    return tensors

def maxIndexOfScores(scores):
    #get the max similarity
    maxSimilarity = max([ torch.max(l).item() for l in scores ])
    #get the index of the max similarity 
    for i in range(len(scores)):
        for j in range(len(scores[i])):
            if scores[i][j] == maxSimilarity:
                return j,maxSimilarity

def diagnosis(testResult):
    total = sum(testResult)
    print('******************************')
    print(total, 'points')
    print('Diagnosis: ')
    if total >= 0 and total <= 10:
        print('These ups and downs are considered normal')
    elif total >= 11 and total <= 16:
        print("Mild mood disturbance")
    elif total >= 17 and total <= 20:
        print("Borderline clinical depression")
    elif total >= 21 and total <= 30:
        print("Moderate depression")
    elif total >= 21 and total <= 40:
        print("Severe depression")
    else:
        print("Extreme depression")
    print('******************************')

################################################################################################

#createEmbeddings(intensityFile,mode='intensity')
sad = ['i feel very tired','i want to commit suicide']
happy = ['i love my life','i sleep very well']
#sentencePresence(sad,printFlag=False)
#sentenceIntensity(happy,printFlag=True,threshold=0.35)
#processJson("rd_depression_2022_11_24_17_10_12_965065_output.json")
#analyzer("rd_2022_10_3_18_37_13_878_output.json")
#analyzer("tw_2022_10_3_19_5_54_567_output_1.json",source='twitter',mode='intensity')
#findMaxIndex()

# tensors = torch.tensor([[0.1599, 0.1370, 0.1933, 0.2030],
#         [0.5391, 0.5128, 0.5068, 0.5192]])
# filtered_tensors = filterBelowThreshold(tensors, 0.25)
# print(filtered_tensors)

#print(jsonToObjectArray("rd_2022_11_0_17_54_31_107_output.json"))
#weekAnalyzer("tw_2022_11_6_12_55_47_611_output.json",mode='twitter')
#timeAnalyzer("rd_2022_11_0_17_54_31_107_output.json",mode='intensity')
#writeEmbeddings()
#readEmbeddings()










    
    