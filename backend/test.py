from sentence_transformers import SentenceTransformer,util
import pickle
import torch
import json
import datetime
model = SentenceTransformer('all-MiniLM-L6-v2')
presenceFile = r".\BDI\bdi_presence.txt"
intensityFile = r".\BDI\bdi_intensity.txt"

def writeEmbeddings():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentences = ['This framework generates embeddings for each input sentence',
        'Sentences are passed as a list of string.', 
        'The quick brown fox jumps over the lazy dog.']
    numbers = [1,2,3]

    embeddings = model.encode(sentences)
    #Store sentences & embeddings on disc
    with open('embeddings.pkl', "wb") as fOut:
        pickle.dump({'sentences': sentences, 'embeddings': embeddings, 'numbers':numbers}, fOut, protocol=pickle.HIGHEST_PROTOCOL)

def readEmbeddings():
    #Load sentences & embeddings from disc
    with open('embeddings.pkl', "rb") as fIn:
        stored_data = pickle.load(fIn)
        stored_sentences = stored_data['sentences']
        stored_embeddings = stored_data['embeddings']
        stored_numbers = stored_data['questionNumbers']
        # print("Embeddings:")
        # print(stored_sentences)
        # print("*******************************")
        # print(stored_embeddings)
        # print("*******************************")
        # print(stored_numbers)
    
    #iterate to group the info of each question in an independent array
    #results will be a list of lists
    sentences = []
    currentQuestionSentences = []
    embeddings = []
    currentQuestionEmbeddings = []
    questionIndex = 1
    for sentence,embedding,questionNumber in zip(stored_sentences,stored_embeddings,stored_numbers):
        #print(questionIndex,questionNumber)
        if questionIndex == questionNumber:
            currentQuestionSentences.append(sentence)
            currentQuestionEmbeddings.append(embedding)
        else:
            questionIndex += 1
            sentences.append(currentQuestionSentences)
            embeddings.append(currentQuestionEmbeddings)
            currentQuestionSentences = []
            currentQuestionEmbeddings = []
            currentQuestionSentences.append(sentence)
            currentQuestionEmbeddings.append(embedding)

    currentQuestionSentences.append(sentence)
    currentQuestionEmbeddings.append(embedding)
    print("*******************************")
    print(embeddings)
    print("********************************")
    print(sentences)
    return embeddings,sentences


def createEmbeddings(file,mode='presence'):
    #list of the embeddings for each question
    embeddings = []
    #list of every sentence
    sentences = []
    #list of the corresponding question of every sentence
    questionNumbers = []
    #list of every option of every question
    questions = []
    #points of every answer
    points = []
    #embeddings of the sentences of a question
    currentQuestion = []
    #points of the sentences of a question
    currentQuestionPoints = []
    #question index to identify each sentence with its question
    questionIndex = 1
    #read BDI file
    with open(file) as f:
        lines = f.read().splitlines()
    
    for l in lines:
        if l != '#':
            if(mode=='presence'):
                sentences.append(l)
                questionNumbers.append(questionIndex)
            else:
                currentQuestionPoints.append(l.split("|")[0])
                currentQuestion.append(l.split("|")[1])
        else:
            questionIndex += 1

    embeddings = model.encode(sentences, convert_to_tensor=True)
            
    #Store sentences & embeddings on disc
    with open('embeddings.pkl', "wb") as fOut:
        pickle.dump({'sentences': sentences, 'embeddings': embeddings, 'questionNumbers':questionNumbers}, fOut, protocol=pickle.HIGHEST_PROTOCOL)


def sentencePresence(sentences,printFlag=False):
    presenceEmbeddings,questions = readEmbeddings()
    print("Questions")
    print(questions)
    print("PrevalenceEmbeddings")
    print(presenceEmbeddings)
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

#createEmbeddings(presenceFile,mode='presence')
#readEmbeddings()

sad = ['i feel very tired','i want to commit suicide']
happy = ['i love my life','i sleep very well']
sentencePresence(sad,printFlag=False)