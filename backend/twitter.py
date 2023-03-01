import crawler

def twitterCrawler(args):
    keyword,username,language,limit,since,until,coordinates = getParams(args)
    outputName = crawler.twitterCrawler(search=keyword,
                            username=username, 
                            language=language, 
                            limit=limit, 
                            since=since, 
                            until=until, 
                            coordinates=coordinates)
    return outputName

def getParams(args):
    keyword = args.get('keyword')
    if keyword == '':
        keyword = None
    username = args.get('username')
    if username == '':
        username = None
    language = args.get('language')
    if language == '':
        language = 'es'
    limit = int(args.get('limit'))
    
    since = args.get('since')
    if since == '':
        since = None
    until = args.get('until')
    if until == '':
        until = None
    coordinates = args.get('coordinates')
    if coordinates == '':
        coordinates = None
    return keyword,username,language,limit,since,until,coordinates