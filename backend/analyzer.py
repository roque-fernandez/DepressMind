from sentence_transformers import SentenceTransformer,util, CrossEncoder
from scipy.special import softmax
import torch
import json
import datetime
import time
import nltk

model = SentenceTransformer('all-MiniLM-L6-v2')
presenceFile = r"./BDI/bdi_presence.txt"
intensityFile = r"./BDI/bdi_intensity.txt"
outputLocation = r"./upload/"
threshold = 0.35

ENTAIL_MODEL = CrossEncoder('cross-encoder/nli-deberta-v3-base')
LABEL_MAPPING = ['contradiction', 'entailment', 'neutral']

bdiTitles = ['Sadness','Pessimism','Past Failure','Loss of Pleasure','Guilty Feelings','Punishment Feelings','Self-Dislike','Self-Criticalness','Suicidal Thoughts or Wishes','Crying','Agitation','Loss of Interest','Indecisiveness','Worthlessness','Loss of Energy','Changes in Sleeping Pattern','Irritability','Changes in Appetite','Concentration Difficulty','Tiredness or Fatigue','Loss of Interest in Sex']

#class used to wrap most intense sentences and its info
class sentenceContext:
    def __init__(self, sentence, link, prevContext=None, folContext=None):
        self.sentence = sentence
        self.link = link
        self.prevContext = prevContext
        self.folContext = folContext
    
    def to_dict(self):
        return { "sentence":self.sentence,"link":self.link,"prevContext":self.prevContext,"folContext":self.folContext}
    
    def __str__(self):
        prevSentence = self.prevContext
        folSentence = self.folContext
        if self.prevContext == None:
            prevSentence = ""
        if self.folContext == None:
            folSentence = ""
        sentenceInfo = "[ Sentence:" + self.sentence + ", Link:" + self.link + ", Prev:" + prevSentence + ", Fol:" + folSentence + " ]"
        return sentenceInfo
        
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
    #create embeddings
    if mode == 'presence':
        presenceEmbeddings,questions = createEmbeddings(presenceFile)
    else:
        intensityEmbeddings,points,questions = createEmbeddings(intensityFile,mode='intensity')

    print("\n********************************")
    print("TEMPORAL ANALYSIS")
    #get results for each time period
    for key in months:
        if mode == 'presence':
            results = sentencePresence(months[key],presenceEmbeddings,questions)
        else:
            results = sentenceIntensity(months[key],intensityEmbeddings,points,questions,threshold=threshold)
        monthlyAnalysis[str(key)] = results

    for key in weeks:
        if mode == 'presence':
            results = sentencePresence(weeks[key],presenceEmbeddings,questions)
        else:
            results = sentenceIntensity(weeks[key],intensityEmbeddings,points,questions,threshold=threshold)
        weeklyAnalysis[str(key)] = results

    for key in days:
        if mode == 'presence':
            results = sentencePresence(days[key],presenceEmbeddings,questions)
        else:
            results = sentenceIntensity(days[key],intensityEmbeddings,points,questions,threshold=threshold)
        dailyAnalysis[str(key)] = results

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
    texts,links = getTextFromJson(file,source=source)
    sentences = []
    #dictionary where the key is the index of the sentence the value is the context of that sentence
    contextDict = {}
    stId = 0
    #create dictionary of context and list of sentences
    for i,t in enumerate(texts):
        splittedText = nltk.sent_tokenize(t)
        for j,st in enumerate(splittedText):
            #append sentence to the list
            sentences.append(st)
            #CONTEXT
            previousSentence = ""
            followingSentence = ""
            #previous
            if j > 0:
                previousSentence =  splittedText[j - 1]
            #following
            if j < (len(splittedText)-1):
                followingSentence = splittedText[j + 1]
            #the index of the text is the same of the link
            sentenceLink = links[i]
            #add object to dictionary
            sentenceObject = sentenceContext(st,sentenceLink,prevContext=previousSentence,folContext=followingSentence)
            contextDict[stId] = sentenceObject
            stId+=1

    print("****************************")   
    print("CONTEXT DICT")
    for key, value in contextDict.items():
        print("Id: ",key)
        print("Value: ")
        print(value.__str__())
        print("------------------")
    
    if mode == 'presence':
        presenceEmbeddings,questions = createEmbeddings(presenceFile)
        result = sentencePresence(sentences,presenceEmbeddings,questions)
        return result 
    else:
        presenceEmbeddings,questions = createEmbeddings(presenceFile)
        intensityEmbeddings,points,questions = createEmbeddings(intensityFile,mode='intensity')
        result,intenseSentences = sentenceIntensityNLI(sentences,points,questions,presenceEmbeddings)
        intenseSentencesContext = getSentenceContext(intenseSentences,sentences,contextDict)
        print("****************************")
        print("RESULTS")
        for i in range(len(intenseSentencesContext)):
            print("----------------------------------")
            print("Question:",bdiTitles[i])
            print("Score:",result[i])
            print("Intense sentence with 1 point:\n",intenseSentencesContext[i][0])
            print("Intense sentence with 2 points:\n",intenseSentencesContext[i][1])
            print("Intense sentence with 3 points:\n",intenseSentencesContext[i][2])
        
        
        return result, intenseSentencesContext

#given a list of texts it creates a dictionary where the key is the index of the sentence
#the value is the context of that sentence
def getDictOfContext(texts,links):  
    contextDict = {}
    stId = 0
    for i,t in enumerate(texts):
        splittedText = nltk.sent_tokenize(t)
        for j,st in enumerate(splittedText):
            previousSentence = None
            followingSentence = None
            #previous
            if j > 0:
                previousSentence =  st[j - 1]
            #following
            if j < (len(st)-1):
                followingSentence = st[j + 1]
            #the index of the text is the same of the link
            sentenceLink = links[i]
            #add object to dictionary
            sentenceObject = sentenceContext(st,sentenceLink,prevContext=previousSentence,folContext=followingSentence)
            contextDict[stId] = sentenceObject
            stId+=1
    return contextDict

#given the most intense sentences of each dimension it returns for every sentence
#the context stored in the contextDictionary
def getSentenceContext(intenseSentences,sentences,contextDict):
    result = []
    for question in intenseSentences:
        #list that contains a list from 1 to 3 points
        questionSentences = [ [], [], [] ]
        #loop used to get into the 3 lists of each question
        for i in range(3):
            for st in question[i]:
                #we get the index of the sentence and get the context from the dict
                index = sentences.index(st)
                questionSentences[i].append(contextDict[index].to_dict())
        result.append(questionSentences)
    return result

def getTextFromJson(file,source='reddit'):
    path = outputLocation + file
    with open(path, encoding="utf8") as f:
        content = f.read()
        decoder = json.JSONDecoder()
        texts = []
        links = []
        while content:
            value, new_start = decoder.raw_decode(content)
            content = content[new_start:].strip()
            # You can handle the value directly in this loop:
            if source == 'reddit':
                text = value['text']
                link = value['link']
            else: 
                text = value['tweet']
            # Or you can store it in a container and use it later:
            texts.append(text)
            links.append(link)
    return texts,links

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

def sentencePresence(sentences,presenceEmbeddings,questions,printFlag=False):
    sentencesEmbedding = model.encode(sentences, convert_to_tensor=True)
    result = []
    questionIndex = 0
    for questionEmbeddings in presenceEmbeddings:
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

def sentenceIntensity(sentences,intensityEmbeddings,points,questions,printFlag=False,threshold=0.2):
    sentencesEmbedding = model.encode(sentences, convert_to_tensor=True)
    result = []
    questionIndex = 0
    for questionEmbeddings in intensityEmbeddings:
        
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
            print('Question:',bdiTitles[questionIndex])
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
    #diagnosis(result)
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

#given the scores of a list of sentences returns the sentences wich have
#the max intensity with the link and context of the sentence
def getMostIntenseSentences(scores,sentences,points,maxPoints,questionIndex):
    mostIntenseSentences = []
    #if there is no points above 0 we return []
    if maxPoints == 0:
        return mostIntenseSentences
    #get points for every sentence
    for i in range(len(sentencePoints)):
        if sentencePoints[i] == maxPoints:
            mostIntenseSentences.append(sentences[i])
    return mostIntenseSentences

#given the scores of a list of sentences and a question
#returns the points for everySentence
def getSentencesPoints(scores,points,maxPoints,questionIndex):
    #get the question option that matches that score
    questionOptions = [torch.argmax(l).item() for l in scores ]
    #get the points for the question option
    sentencesPoints = [ int(points[questionIndex][questionOption]) for questionOption in questionOptions ]
    print("Question options: ",questionOptions)
    print("Question points: ",sentencesPoints)
    return 

#############################################################################################################  
# INTENSITY USING NATURAL LANGUAGE INFERENCE
############################################################################################################# 

def sentenceIntensityNLI(sentences,points,questions,presenceEmbeddings,printFlag=False,threshold=0.35):
    sentencesEmbedding = model.encode(sentences, convert_to_tensor=True)
    result = []
    mostIntenseSentences = []
    questionIndex = 0
    for questionEmbeddings in presenceEmbeddings:
        nAboveThreshold = 0
        nEntailments = 0
        #print("************************************")
        #print('Question:',bdiTitles[questionIndex])
        #Compute cosine-similarities
        cosineScores = util.cos_sim(sentencesEmbedding, questionEmbeddings)
        #get the max similarity of every sentence within a question
        maxPresence = [torch.max(l).item() for l in cosineScores]
        #filter sentences with a presence below the filter
        filteredSentences = []
        #print("FILTERED SENTENCES")
        for i,p in enumerate(maxPresence):
            if p > threshold:
                nAboveThreshold += 1
                filteredSentences.append(sentences[i]) 
                if printFlag:
                    print(sentences[i], " [ ", p , " ] ")
        #apply entailment model to filtered sentences
        questionResults = []
        #print("ENTAILMENTS")
        for st in filteredSentences:
            #array where the scores of a sentence for the options of the question
            sentenceValuesForQuestion = []
            for option in questions[questionIndex]:
                score = ENTAIL_MODEL.predict([(st, option)]) ### text, hypothesis => it is very important to keep the order
                label =  [LABEL_MAPPING[score_max] for score_max in score.argmax(axis=1)]   
                if label[0] == 'entailment':
                    value = softmax(score[0])[1]
                    nEntailments += 1
                    if printFlag:
                        print("{} \t {} \t Score: {} \t Value: {:.2f} \t Label: {}".format(st, option, score, value, label))
                else:
                    value = -1
                sentenceValuesForQuestion.append(value)       
            questionResults.append(sentenceValuesForQuestion)
                
        #get the most intense sentences for the question and append it and the maxPoints
        questionIntenseSentences,maxPoints = intenseSentencesOfQuestion(questionResults,sentences,points,questionIndex)
        mostIntenseSentences.append(questionIntenseSentences)
        result.append(maxPoints)
        print("Intensity for question:",maxPoints)

        questionIndex += 1

    print("Result: \n",result)
    print("Intense sentences: \n",mostIntenseSentences)
    return result,mostIntenseSentences
            
#given the scores of the sentences with the options of a question 
#returns the index of the max value
def maxIndexOfScoresNLI(scores):
    maxSimilarity = scores[0][0]
    maxSimilarityIndex = 0
    #get the index of the max similarity 
    for i in range(len(scores)):
        for j in range(len(scores[i])):
            #if there is a tie we get the last value
            if scores[i][j] >= maxSimilarity and scores[i][j] > 0:
                maxSimilarity = scores[i][j]
                maxSimilarityIndex = j
    return maxSimilarityIndex,maxSimilarity 

#given the scores of a list of sentences returns the sentences wich have
#the max intensity for a question (including sentences with 1 to 3 points) 
def intenseSentencesOfQuestion(scores,sentences,points,questionIndex):
    #list that contains a list from 1 to 3 points
    mostIntenseSentences = [ [],[],[] ]
    #get points for every sentence
    sentencesPoints = getSentencesPointsNLI(scores,points,questionIndex)
    maxPoints = max(sentencesPoints)
    #if there is no points above 0 we return empty
    if maxPoints == 0:
        return mostIntenseSentences,maxPoints
    
    for i in range(len(sentencesPoints)):
        #1 point
        if sentencesPoints[i] == 1:
            mostIntenseSentences[0].append(sentences[i])
        #2 points
        elif sentencesPoints[i] == 2:
            mostIntenseSentences[1].append(sentences[i])
        #3 points
        elif sentencesPoints[i] == 3:
            mostIntenseSentences[2].append(sentences[i])
    return mostIntenseSentences,maxPoints

#given the scores of a list of sentences and a question
#returns the points for everySentence
def getSentencesPointsNLI(scores,points,questionIndex):
    #get the question option that matches that score
    #if there is a tie we get the last value
    #if max is -1 we dont have an entailment so we filter it
    # Reverse the list and get the last index of the element
    questionOptions = [ (len(l) - l[::-1].index(max(l)) - 1) for l in scores if max(l) > -1 ]
    #get the points for the question option
    sentencesPoints = [ int(points[questionIndex][questionOption]) for questionOption in questionOptions ]
    if len(sentencesPoints) == 0:
        sentencesPoints = [0]
    # print("Question points: ",sentencesPoints)
    return sentencesPoints
    
# ==========================================================================================================================












    
    