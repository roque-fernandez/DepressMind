import twint
import requests
import json
import sys
import re
import os
from datetime import datetime
from bs4 import BeautifulSoup

outputFolder='outputs'

########################################################################################################################

def twitterHeader(search, username, language, limit, since, until, coordinates, outfile):
    print("***********************************************************************")
    print("***********************************************************************\n")
    print("TWITTER CRAWLER")
    print("Currently searching ", search, ' || Username: ', username)
    print("Getting", limit, "tweets", since, ' to ', until)
    print("Language: ", language, ' || Coordinates: ', coordinates)
    print("Results available at", outfile, "\n")
    print("***********************************************************************")
    print("***********************************************************************\n")

def twitterCrawler(search=None, username=None, language='es', limit=100, since=None, until=None, coordinates=None):
    fileUsername = ''
    fileSearch = ''
    c = twint.Config()
    if search is not None:
        c.Search = search
        fileSearch = '_' + search
    if username is not None:
        c.Username = username
        fileUsername = '_' + username
    c.Lang = language
    c.Limit = limit
    if since is not None:
        c.Since = since
    if until is not None:
        c.Until = until
    if coordinates is not None:
        c.Geo = coordinates
    c.Custom['tweet'] = ['username','tweet','date','time','id','name','language','replies_count','retweets_count','likes_count','link','geo']
    # storing data to a json file
    c.Store_json = True
    outfile = "tw" + fileSearch + fileUsername + "_" + datetime.today().strftime('%Y_%m_%d_%H_%M_%S_%f') + "_output.json"
    c.Output = './'+ outputFolder + '/' + outfile
    # printing execution info
    twitterHeader(search, username, language, limit, since, until, coordinates, outfile)
    # running search
    twint.run.Search(c)
    return outfile

########################################################################################################################

class redditPost:
    def __init__(self, username, text, date=None, votes=None, link=None):
        self.username = username
        self.text = text
        self.date = date
        self.votes = votes
        self.link = link

def getPostInfo(soup):
    postVotes = soup.find("div", class_="score unvoted").text
    usernameRegex = re.compile('.*author.*')
    postUsername = soup.find("a", {"class" : usernameRegex}).text
    postText = soup.find("a", {"class": ["title may-blank", "title may-blank outbound"]}).text.strip()
    postText += " "

    if soup.find("div", class_="md") is not None:
        postText += soup.find("div", class_="md").text.strip()
    postDate = soup.find("time")["datetime"]
    if postVotes == "•":
        postVotes = 0

    postLink = "https://reddit.com" + soup.find("div", class_="thing")["data-url"]

    return redditPost(postUsername, postText, postDate, postVotes, postLink)

def writePostToJson(post, outfile):
    jsonPost = json.dumps(post.__dict__, indent=1)
    outfile.write(jsonPost)
    print("_________________")
    print(jsonPost)
    print("_________________")

def getCommentInfo(soup,link=None):
    usernameRegex = re.compile('.*author.*')
    commentUsername = soup.find("a", {"class": usernameRegex}).text
    commentText = soup.find("div", class_="usertext-body").text.strip()
    commentDate = soup.find("time")["datetime"]
    commentLink = "https://reddit.com" + link

    return redditPost(commentUsername, commentText, commentDate, link=commentLink)

def dateInRange(since, until, date):
    if date > since and date < until:
        return True
    return False

def redditDateToTimestamp(date):
    date = date.split("+")[0]
    element = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    return datetime.datetime.timestamp(element)

def redditHeader(query, limit, votes, since, until, outfile):
    print("***********************************************************************")
    print("***********************************************************************\n")
    print("REDDIT CRAWLER")
    print("Currently crawling " + query)
    print("Getting", limit, "posts , with at least ", votes, ' upvotes, since ', since, ' to ', until)
    #print("Results available at", query + "_output.json\n")
    print("***********************************************************************")
    print("***********************************************************************\n")

def subredditCrawler(subreddit, limit=1000, votes=0, since=None, until=None, outputName=None):
    try:
        url = 'https://old.reddit.com/r/' + subreddit
        if since is None:
            since = "1970-01-01"
        if until is None:
            until = datetime.today().strftime('%Y-%m-%d')

        writingMode = 'a'

        # Headers to mimic a browser visit
        headers = {'User-Agent': 'Mozilla/5.0'}

        # Returns a requests.models.Response object
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        #check if subreddit exists
        if not soup.find("body", class_="listing-page"):
            raise Exception("{} subreddit does not exist".format(subreddit))

        # giving name to the output
        if outputName is None:
            outputName = "rd_" + subreddit + "_" + datetime.today().strftime('%Y_%m_%d_%H_%M_%S_%f') + "_output.json"
            writingMode = 'w'

        # printing information
        redditHeader(subreddit, limit, votes, since, until, outputName)

        count = 0
        invalidLinkCount = 0
        invalidLinkLimit = 25

        with open(os.path.join(os.path.expanduser('.'),outputFolder,outputName), writingMode) as outfile:

            while count <= limit:

                # get links to the comments of every post in the main page
                for link in soup.findAll("a", {"class": ["title may-blank", "title may-blank outbound"]}):
                    postLink = link.get("href")
                    print("Postlink: ",postLink)

                    if postLink.split("/")[0] == "https:":
                        print("Not valid link: ",postLink)
                        invalidLinkCount+=1
                        if invalidLinkCount > invalidLinkLimit:
                            print("This subreddit probably contains only links.")
                            return count,outputName
                        continue

                    commentsPageUrl = 'https://old.reddit.com' + postLink
                    invalidLinkCount = 0
                    print(commentsPageUrl)

                    try:
                        commentsPage = requests.get(commentsPageUrl, headers=headers)
                        commentsPageSoup = BeautifulSoup(commentsPage.text, 'html.parser')

                        # POST
                        postSoup = commentsPageSoup.find("div", class_="sitetable linklisting")
                        post = getPostInfo(postSoup)
                        print("Post initiated")


                        if int(post.votes) < votes:
                            continue
                        if not dateInRange(since, until, post.date):
                            continue
                        # check limit
                        if count >= limit:
                            print("Limit reached at ", count, " posts")
                            return count,outputName
                        print("Post: ", post.username)

                        # writing the object to json file
                        writePostToJson(post, outfile)
                        count += 1
                    except Exception as e:
                        print("Error ocurred getting post info: ",e)

                    # COMMENTS OF THE POST
                    # we dont want the first comment because it is the title
                    for commentSoup in commentsPageSoup.findAll("div", class_="entry unvoted")[1:]:
                        # check if is a valid comment (not deleted)
                        taglineContent = commentSoup.find("p", class_="tagline").text

                        if (taglineContent and not "[deleted]" in taglineContent):
                            try:
                                comment = getCommentInfo(commentSoup,link=postLink)

                                if not dateInRange(since, until, comment.date):
                                    continue
                                # check limit
                                if (count >= limit):
                                    print("LIMIT REACHED ", count, " posts")
                                    return count,outputName

                                # writing the object to json file
                                writePostToJson(comment, outfile)

                                count += 1
                            except Exception as e:
                                print("Error ocurred getting comment info: ",e)
                    print("N comments written:", count)

                    # move to the next page of the subreddit
                    if soup.find("a", rel="nofollow next") is not None:
                        newUrl = soup.find("a", rel="nofollow next").get("href")
                        print("New url: ", newUrl)
                        page = requests.get(newUrl, headers=headers)
                        soup = BeautifulSoup(page.text, 'html.parser')
                    else:
                        print("Last page of subreddit")
                        return count,outputName
    except Exception as e:
        print("Error ocurred crawling subreddit: ",e)

def redditGeneralistCrawler(limit=1000, limitPerSubreddit=50, votes=0, since=None, until=None):
    url = 'https://old.reddit.com/new/'
    # Headers to mimic a browser visit
    headers = {'User-Agent': 'Mozilla/5.0'}
    # Returns a requests.models.Response object
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    count = 0
    outputName = "rd_generalist_" + datetime.today().strftime('%Y_%m_%d_%H_%M_%S_%f') + "_output.json"
    if limit < limitPerSubreddit:
        limitPerSubreddit = limit

    while count <= limit:

        # get links to the comments of every post in the main page
        for link in soup.findAll("a", class_="subreddit hover may-blank"):
            subreddit = link.text
            subreddit = subreddit.split("/")[-1]
            # print("Next subreddit: ", subreddit)
            # print("*****************")
            nWrittenPosts = subredditCrawler(subreddit, limitPerSubreddit, votes=votes, since=since, until=until, outputName=outputName)[0]
            count += nWrittenPosts
            if (count > limit):
                return outputName

        # move to the next page
        newUrl = soup.find("a", rel="nofollow next").get("href")
        page = requests.get(newUrl, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
    return outputName

def getUserPostInfo(soup):
    usernameRegex = re.compile('.*author.*')
    usernameSoup = soup.find("p", class_="tagline")
    postUsername = usernameSoup.find("a", {"class": usernameRegex}).text
    postText = soup.find("a", {"class": ["title", "title may-blank", "title may-blank outbound"]}).text.strip()
    postText += " "
    if soup.find("div", class_="md") is not None:
        postText += soup.find("div", class_="md").text.strip()
    postDate = soup.find("time")["datetime"]
    postVotes=0
    #check if post has valid votes
    if soup.find("div", class_="midcol unvoted").text != "":
        postVotes = soup.find("div", class_="score unvoted").text
    postLink = "https://reddit.com" + soup.find("a", {"class": ["title"]})["href"]
    
    return redditPost(postUsername, postText, postDate, postVotes, postLink)

def redditUserCrawler(username, limit=1000, votes=0, since=None, until=None):
    url = 'https://old.reddit.com/user/' + username
    outputName = "rd_user_" + username + "_" + datetime.today().strftime('%Y_%m_%d_%H_%M_%S_%f') + "_output.json"
    if since is None:
        since = "1970-01-01"
    if until is None:
        until = datetime.today().strftime('%Y-%m-%d')

    # printing information
    redditHeader(username, limit, votes, since, until, outputName)

    # Headers to mimic a browser visit
    headers = {'User-Agent': 'Mozilla/5.0'}
    # Returns a requests.models.Response object
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    #check if user exists
    if not soup.find("body", class_="listing-page"):
        raise Exception("{} is not a valid user".format(username))

    count = 0

    with open(os.path.join(os.path.expanduser('.'),outputFolder,outputName), 'w') as outfile:
        while count <= limit:
            postsRegex = re.compile('.*thing.*')
            for postSoup in soup.findAll("div", {"class" : postsRegex}):
                # check if is a valid comment (not deleted)
                taglineContent = postSoup.find("p", class_="tagline").text
                if (taglineContent and not "[deleted]" in taglineContent):
                    try:
                        post = getUserPostInfo(postSoup)

                        print("Post:", post.text , "||",post.username,"||",post.date)
                        
                        #check votes and dates
                        if int(post.votes) < votes:
                            continue
                        if not dateInRange(since, until, post.date):
                            continue
                        if post.username != username:
                            continue
                        # check limit
                        if count >= limit:
                            print("LIMIT REACHED ", count, " posts")
                            return count,outputName

                        # writing the object to json file
                        writePostToJson(post, outfile)

                        count += 1
                    except Exception as e:
                        print("Error ocurred getting userPost info: ", e)

        # move to the next page of the subreddit
        if soup.find("a", rel="nofollow next") is not None:
            newUrl = soup.find("a", rel="nofollow next").get("href")
            print("New url: ", newUrl)
            page = requests.get(newUrl, headers=headers)
            soup = BeautifulSoup(page.text, 'html.parser')
            print("New page")
        else:
            print("Last page")
            return count,outputName

def getQueryPostInfo(soup):
    usernameRegex = re.compile('.*author.*')
    postUsername = soup.find("a", {"class": usernameRegex}).text
    titleRegex = re.compile('.*search-title.*')
    postText = soup.find("a", {"class":titleRegex}).text.strip()
    postText += " "
    if soup.find("div", class_="md") is not None:
        postText += soup.find("div", class_="md").text.strip()
    postDate = soup.find("time")["datetime"]
    postVotes = soup.find("span", class_="search-score").text.split(" ")[0]
    postVotes = postVotes.translate({ord(c): None for c in ",\""})
    postLink = "https://reddit.com" + soup.find("a", {"class": ["may-blank thumbnail"]})["href"]
    return redditPost(postUsername, postText, postDate, postVotes, postLink)

def redditQueryCrawler(query, limit=1000, votes=0, since=None, until=None):
    url = 'https://old.reddit.com/search?q=' + query
    outputName = "rd_query_" + query + "_" + datetime.today().strftime('%Y_%m_%d_%H_%M_%S_%f') + "_output.json"
    if since is None:
        since = "1970-01-01"
    if until is None:
        until = datetime.today().strftime('%Y-%m-%d')

    # printing information
    redditHeader(query, limit, votes, since, until, outputName)

    # Headers to mimic a browser visit
    headers = {'User-Agent': 'Mozilla/5.0'}
    # Returns a requests.models.Response object
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    #check if query has results
    if not soup.find("div", class_="search-result"):
        raise Exception("The search returned no results for {} query".format(query))

    count = 0

    with open(os.path.join(os.path.expanduser('.'),outputFolder,outputName), 'w') as outfile:
        while count <= limit:
            postsRegex = re.compile('.*search-result-link.*')
            for postSoup in soup.findAll("div", {"class" : postsRegex}):
                try:
                    post = getQueryPostInfo(postSoup)

                    if not dateInRange(since, until, post.date):
                        continue
                    # check limit
                    if count >= limit:
                        print("LIMIT REACHED ", count, " posts")
                        return count,outputName

                    # writing the object to json file
                    writePostToJson(post, outfile)

                    count += 1
                except Exception as e:
                    print("Error ocurred getting userPost info: ", e)

        # move to the next page of the subreddit
        if soup.find("a", rel="nofollow next") is not None:
            newUrl = soup.find("a", rel="nofollow next").get("href")
            print("New url: ", newUrl)
            page = requests.get(newUrl, headers=headers)
            soup = BeautifulSoup(page.text, 'html.parser')
            print("New page")
        else:
            print("Last page")
            return count,outputName

########################################################################################################################

def commandLineParser():
    args = sys.argv[1:]

    # twitter command
    if args[0] == 'tw':
        search = None
        username = None
        language = 'es'
        limit = 3000
        since = None
        until = None
        coord = None
        for i in range(len(args)):
            if args[i] == '-s':
                search = args[i + 1]
            if args[i] == '-u':
                username = args[i + 1]
            if args[i] == '-la':
                language = args[i + 1]
            if args[i] == '-l':
                limit = int(args[i + 1])
            if args[i] == '-si':
                since = args[i + 1]
            if args[i] == '-un':
                until = args[i + 1]
            if args[i] == '-c':
                coord = args[i + 1]
        twitterCrawler(search=search, username=username, language=language, limit=limit, since=since, until=until,
                       coordinates=coord)

    # reddit command
    elif args[0] == 'rd':
        subreddit = args[1]
        limit = 1000
        votes = 0
        since = None
        until = None
        for i in range(len(args)):
            if args[i] == '-v':
                votes = int(args[i + 1])
            if args[i] == '-l':
                limit = int(args[i + 1])
            if args[i] == '-si':
                since = args[i + 1]
            if args[i] == '-un':
                until = args[i + 1]
        subredditCrawler(subreddit, limit=limit, votes=votes, since=since, until=until)
    else:
        print("Error")

########################################################################################################################
#commandLineParser()
#subredditCrawler('depression',votes=0,limit=1000)
#subredditCrawler('depression_help',votes=0,limit=100)

#prueba()
# getLink()
#twitterCrawler(username="roquefernandez_",search="chorizo",limit=100)
#redditGeneralistCrawler(limit=100, limitPerSubreddit=20)
#redditUserCrawler('toohottooheavy',limit=10)
#redditQueryCrawler("car",limit=50)
