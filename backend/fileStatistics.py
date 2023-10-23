import json
outputLocation = r"./outputs/"

def redditStatistics(file):
    path = outputLocation + file
    with open(path, encoding="utf8") as f:
        content = f.read()
        decoder = json.JSONDecoder()
        users = []
        total = 0
        totalVotes = 0
        while content:
            value, new_start = decoder.raw_decode(content)
            content = content[new_start:].strip()
            # You can handle the value directly in this loop:
            #print("Parsed:", value['votes'])
            # Or you can store it in a container and use it later:
            users.append(value['username'])
            if value['votes']==None:
                votes = 0
            else:
                votes = int(value['votes'])
            totalVotes += votes
            total+=1

        totalUsers = len(set(users))
        avgVotes = totalVotes/total
        print("Posts:",total," || Avg. votes:",avgVotes, " || N of users:",totalUsers)
        return total,avgVotes,totalUsers

def twitterStatistics(file):
    path = outputLocation + file
    with open(path, encoding="utf8") as f:
        content = f.read()
        decoder = json.JSONDecoder()
        users = []
        total = 0
        totalLikes = 0
        totalRts = 0
        while content:
            value, new_start = decoder.raw_decode(content)
            content = content[new_start:].strip()
            # You can handle the value directly in this loop:
            #print("Parsed:", value['username'])
            # Or you can store it in a container and use it later:
            users.append(value['username'])
            totalLikes += value['likes_count']
            totalRts += value['retweets_count']
            total+=1

        totalUsers = len(set(users))
        avgLikes = totalLikes/total
        avgRts = totalRts/total
        print("Posts:",total," || Avg. likes:",avgLikes, " || Avg. rts:",avgRts, " || N of users:",totalUsers)
        return total,avgLikes,avgRts,totalUsers



#redditStatistics('rd_depression_2022_11_24_17_10_12_965065_output.json')
#twitterStatistics('tw_bread_2022_11_30_18_57_28_778556_output.json')