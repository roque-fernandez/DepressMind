from sentence_transformers import SentenceTransformer,util, CrossEncoder
from scipy.special import softmax
import torch
import json
import datetime
import time
import nltk

model = SentenceTransformer('all-MiniLM-L6-v2')
presenceFile = r".\BDI\bdi_presence.txt"
intensityFile = r".\BDI\bdi_intensity.txt"
outputLocation = r".\upload\\"
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
        sentenceInfo = "[ Sentence:" + self.sentence + ", Link:" + self.link + ", Prev:" + self.prevContext + ", Fol:" + self.folContext + " ]"
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
    print("\n********************************")
    print("TEMPORAL ANALYSIS")
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
    texts,links = getTextFromJson(file,source=source)
    sentencesLinks = []
    sentences = []
    for t,l in zip(texts,links):
        splittedText = nltk.sent_tokenize(t)
        for st in splittedText:
            sentences.append(st)
            sentencesLinks.append(l)
    if mode == 'presence':
        result = sentencePresence(sentences)
        return result 
    else:
        result,intenseSentences = sentenceIntensityNLI(sentences,threshold=threshold)
        intenseSentencesContext = getSentenceContext(intenseSentences,texts,links)
        print("****************************")
        print("RESULTS")
        for i in range(len(intenseSentencesContext)):
            print("Question:",bdiTitles[i])
            print("Score:",result[i])
            print("Intense sentence:",intenseSentencesContext[i])
        return result, intenseSentencesContext  

#given the most intense sentences of each dimension it returns for every sentence
#an object containing the sentence, the link to the post and context
def getSentenceContext(intenseSentences,texts,links):
    result = []
    for question in intenseSentences:
        questionSentences = []
        for sentence in question:
            previousSentence = None
            followingSentence = None
            for text in texts:
                if sentence in text:
                    #get the text where the sentence is written
                    #split text by . get the index of the sentence
                    splittedText = nltk.sent_tokenize(text)
                    currentIndex = splittedText.index(sentence)
                    #previous
                    if currentIndex > 0:
                        previousSentence =  splittedText[currentIndex - 1]
                    #following
                    if currentIndex < (len(splittedText)-1):
                        followingSentence = splittedText[currentIndex + 1]

                    #the index of the text is the same of the link
                    linkIndex = texts.index(text)
                    sentenceLink = links[linkIndex]
            sentenceObject = sentenceContext(sentence,sentenceLink,prevContext=previousSentence,folContext=followingSentence)
            questionSentences.append(sentenceObject.to_dict())
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

def sentencePresence(sentences,printFlag=False):
    prevalenceEmbeddings,questions = createEmbeddings(presenceFile)
    # print("Questions")
    # print(questions)
    # print("PrevalenceEmbeddings")
    # print(prevalenceEmbeddings)
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
    intensityEmbeddings,points,questions = createEmbeddings(intensityFile,mode='intensity')
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
def mostIntenseSentences(scores,sentences,points,maxPoints,questionIndex):
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

def sentenceIntensityNLI(sentences,printFlag=False,threshold=0.2):
    intensityEmbeddings,points,questions = createEmbeddings(intensityFile,mode='intensity')
    #sentencesEmbedding = model.encode(sentences, convert_to_tensor=True)
    totalResults = []
    result = []
    questionIndex = 0
    mostIntenseSentences = []
    
    for question in questions:
        print("************************************")
        print('Question:',bdiTitles[questionIndex])
        questionResults = []
        for sentence in sentences:
            #array where the scores of a sentence for the options of the question
            sentenceValuesForQuestion = []
            for option in question:
                score = ENTAIL_MODEL.predict([(sentence, option)]) ### text, hypothesis => it is very important to keep the order
                label =  [LABEL_MAPPING[score_max] for score_max in score.argmax(axis=1)]   
                #if label is neutral or contradiction we consider the value a 0
                if label[0] != 'entailment':
                    value = 0
                else:
                    value = softmax(score[0][1])
                sentenceValuesForQuestion.append(value)
                
                if printFlag:
                    print("{} \t {} \t Score: {} \t Value: {:.3f} \t Label: {}".format(sentence, option, score, value, label))
                    

            questionResults.append(sentenceValuesForQuestion)

        print("Results for question: \n",questionResults)
        #get points corresponding to that question
        maxSimilarityIndex,maxSimilarity = maxIndexOfScoresNLI(questionResults)
        maxPoints = int(points[questionIndex][maxSimilarityIndex])
        result.append(maxPoints)
        #get the most intense sentences for the question and append it
        mostIntenseSentences.append(intenseSentencesOfQuestion(questionResults,sentences,points,maxPoints,questionIndex))
        totalResults.append(questionResults)
        print("Intensity for question:",maxPoints)
        questionIndex += 1
    #print("Total results:", totalResults)
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
#the max intensity ¿[with the link and context of the sentence]?
def intenseSentencesOfQuestion(scores,sentences,points,maxPoints,questionIndex):
    mostIntenseSentences = []
    #if there is no points above 0 we return []
    if maxPoints == 0:
        return mostIntenseSentences
    #get points for every sentence
    sentencesPoints = getSentencesPointsNLI(scores,points,questionIndex)
    for i in range(len(sentencesPoints)):
        if sentencesPoints[i] == maxPoints:
            mostIntenseSentences.append(sentences[i])
    return mostIntenseSentences

#given the scores of a list of sentences and a question
#returns the points for everySentence
def getSentencesPointsNLI(scores,points,questionIndex):
    #get the question option that matches that score
    #if there is a tie we get the last value
    # Reverse the list and get the last index of the element (all 0 is an exception)
    questionOptions = [ l.index(max(l)) for l in scores ]
    questionOptions = [ (len(l) - l[::-1].index(max(l)) - 1) if max(l)>0 else 0 for l in scores ]
    #get the points for the question option
    sentencesPoints = [ int(points[questionIndex][questionOption]) for questionOption in questionOptions ]
    print("Question options: ",questionOptions)
    print("Question points: ",sentencesPoints)
    return sentencesPoints
    
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

def testNLI(sentences,options):
    scores = ENTAIL_MODEL.predict([(sentences, options)]) ### text, hypothesis => it is very important to keep the order
    labels =  [LABEL_MAPPING[score_max] for score_max in scores.argmax(axis=1)]
    print("Scores:", scores)
    print("Labels:", labels)

def comparacionIntensidades(sentences):
    print("*************************************************************************************")
    print("NLI")
    print("*************************************************************************************")
    start_time_1 = time.time()
    sentenceIntensityNLI(sentences,printFlag=True,threshold=0.35)
    end_time_1 = time.time()
    time_1 = end_time_1 - start_time_1
    print("*************************************************************************************")
    print("Normal")
    print("*************************************************************************************")
    start_time_2 = time.time()
    sentenceIntensity(sentences,printFlag=True,threshold=0.35)
    end_time_2 = time.time()
    time_2 = end_time_2 - start_time_2
    print("*************************************************************************************")
    print("Tiempo NLI: ", time_1)
    print("Tiempo normal: ", time_2)
    print("*************************************************************************************")
################################################################################################

#createEmbeddings(intensityFile,mode='intensity')
sad = ['i feel very tired','i want to commit suicide','everything i have done in my life is wrong']
happy = ['i love my life','i sleep as usual']
veryHappy = ['i am happy','i feel great today']
suicidalThoughtsOptions = ["I don't have any thoughts of killing myself.",
                            "I have thoughts of killing myself, but I would not carry them out.",
                            "I would like to kill myself.",
                            "I would kill myself if I had the chance."]

#sentenceIntensityNLI(sad,printFlag=True,threshold=0.35)
#print("*************************************************************************************")
#sentenceIntensity(sad,printFlag=True,threshold=0.35)

#comparacionIntensidades(sad)

#sentencePresence(sad,printFlag=False)
#sentenceIntensity(sad,printFlag=True,threshold=0.35)
#processJson("rd_depression_2022_11_24_17_10_12_965065_output.json")
#analyzer("demo_analyzer_short.json",mode='intensity')
#analyzer("tw_2022_10_3_19_5_54_567_output_1.json",source='twitter',mode='intensity')
#findMaxIndex()

tensors = torch.tensor([[0.1599, 0.1370, 0.1933, 0.2030],
         [0.5391, 0.5128, 0.5068, 0.5192]])

exampleScores = [[0.1599, 0.1370, 0.1933, 0.2030],
         [0.5391, 0.5128, 0.5068, 0.5192]]

#score for veryHappy sentences in question 1 (sadness)
scoreVeryHappyQ1 = torch.tensor([[0.0, 0.0, 0.3541, 0.3585],
         [0.4335, 0.4045, 0.3736, 0.0]])

#testNLI(sad,suicidalThoughtsOptions)


#analyzer('rd_query_car_2023_03_03_16_54_30_307193_output.json',source='reddit',mode='intensity')

#prevalenceEmbeddings,points,questions = createEmbeddings(intensityFile,mode='intensity')

#getSentencesPoints(tensors,points,0,0)
#getSentencesPointsNLI(exampleScores,points,0,0)

# filtered_tensors = filterBelowThreshold(tensors, 0.25)
# print(filtered_tensors)

#print(jsonToObjectArray("rd_2022_11_0_17_54_31_107_output.json"))
#weekAnalyzer("tw_2022_11_6_12_55_47_611_output.json",mode='twitter')
#timeAnalyzer("rd_2022_11_0_17_54_31_107_output.json",mode='intensity')
#writeEmbeddings()
#readEmbeddings()










    
    