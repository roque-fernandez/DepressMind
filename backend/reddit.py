import crawler

def generalistCrawl(args):
    limit,votes,since,until = getParams(args)

    print("Generalist crawl: ")
    print(limit,votes,since,until)
    outputName = crawler.redditGeneralistCrawler(limit=limit,votes=votes,since=since,until=until)
    return outputName

def subredditCrawl(args):
    subreddit = args.get('subreddit')
    limit,votes,since,until = getParams(args)

    print("Subreddit crawl: ")
    print(subreddit,limit,votes,since,until)
    outputName = crawler.subredditCrawler(subreddit,limit=limit,votes=votes,since=since,until=until)[1]
    print("OutputName:",outputName)
    return outputName


def userCrawl(args):
    user = args.get('username')
    limit,votes,since,until = getParams(args)

    print("user crawl: ")
    print(user,limit,votes,since,until)
    outputName = crawler.redditUserCrawler(user,limit=limit,votes=votes,since=since,until=until)[1]
    return outputName

def keywordCrawl(args):
    keyword = args.get('keyword')
    limit,votes,since,until = getParams(args)

    print("Keyword crawl: ")
    print(keyword,limit,votes,since,until)
    outputName = crawler.redditQueryCrawler(keyword,limit=limit,votes=votes,since=since,until=until)[1]
    return outputName

def getParams(args):
    limit = int(args.get('limit'))
    votes = int(args.get('votes'))
    since = args.get('since')
    if since == '':
        since = None
    until = args.get('until')
    if until == '':
        until = None
    return limit,votes,since,until

