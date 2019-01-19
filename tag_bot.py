import praw, time, requests, os, re, datetime, json

# the API URL defined for easy finding and adjustment
API_URL = 'https://nhentai.net/g/'
PARSED_SUBREDDIT = 'Animemes+anime_irl+u_Loli-Tag-Bot+u_nHentai-Tag-Bot'
# PARSED_SUBREDDIT = 'loli_tag_bot'

doNotReplyList = ['AreYouDeaf', 'HelperBot_', 'YTubeInfoBot', 'ghost_of_dongerbot', 'RemindMeBot', 'anti-gif-bot', 'Roboragi', 'shota_bot', 'sneakpeekbot', 'tweettranscriberbot', 'Random_Numbers_Bot', 'WhyNotCollegeBoard', 'nHentai-Tag-Bot', 'EFTBot']
stringsToTags = ['','', 'english', "mind break" , 'rape', "oppai loli", "ugly bastard", 'snuff', 'shota', 'guro', 'scat', 'femdom', 'pregnant', 'inflation', 'futa', 'non-H', 'urination', 'yuri', 'ryona', 'asphyxiation']


def authenticate():
    print("Authenticating...")
    reddit = praw.Reddit('lolitagbot')
    print("Authenticated as {}".format(reddit.user.me()))
    return reddit


# def authenticate():
#     print("Authenticating...")
#     reddit = praw.Reddit('thevexedgermanbot')
#     print("Authenticated as {}".format(reddit.user.me()))
#     return reddit


def main():
    reddit = authenticate()
    commentsRepliedTo = getSavedComments()
    # postsRepliedTo = getSavedPosts()
    while True:
        run_bot(reddit, commentsRepliedTo)


def run_bot(reddit, commentsRepliedTo, postsRepliedTo=[]):
    print("Current time: " + str(datetime.datetime.now().time()))
    print("Fetching comments...")
    # readMessages = []
    # to limit fetched comments use comments(limit=int)
    for comment in reddit.subreddit(PARSED_SUBREDDIT).comments():
        replyString = ""
        cmt = comment.body
        # print(cmt)
        if comment.id not in commentsRepliedTo and comment.author not in doNotReplyList and comment.author != reddit.user.me():
            tagResultCache = getTagResultCache(cmt)
            # Check if tagResultCache is not empty.
            if tagResultCache:
                # if there are 2 or more valid numbers in the list do a special concat
                if len(tagResultCache) > 1:
                    replyString = generateReplyStringMultiple(tagResultCache)
                else:
                    replyString = generateReplyStringSingle(tagResultCache)
            # Check if a reply was generated
            if replyString:
                # post the string and save the replied to comment to not analyse and reply again
                # print("PrePost" + replyString)               
                reply = writeCommentReply(replyString, comment)
                commentsRepliedTo.append(comment.id)
                if len(tagResultCache) == 1:
                    result = tagResultCache[0]
                    tagResult = result[1]
                    if tagResult[4] and not tagResult[3] and not tagResult[11]:
                        reddit.redditor('IsThisLoss1-1i-11-1_').message('SVU Ping', 'https://www.reddit.com'+str(reply.permalink)+'?context=3')
    # do the same for titles as it does for comments
    print("Current time: " + str(datetime.datetime.now().time()))
    print("Fetching posts...")
    for submission in reddit.subreddit(PARSED_SUBREDDIT).new(limit=10):
        replyString = ""
        title = submission.title
        if submission.id not in postsRepliedTo:
            tagResultCache = getTagResultCache(title)
            if tagResultCache:
                replyString = generateReplyStringSingle(tagResultCache)
            if replyString:
                print(replyString)
                postsRepliedTo.append(submission.id)
                submission.reply(replyString)
                # with open("postsRepliedTo.txt", "a") as f:
                #     f.write(comment.id + "\n")
    print("Checking Messages...")
    print("Current time: " + str(datetime.datetime.now().time()))
    #Checks messages
    for message in reddit.inbox.unread(limit=None):
        #Criteria
        usernameMention = message.subject == 'username mention'
        usernameInBody = message.subject == 'comment reply' and "u/{}".format(reddit.user.me()) in message.body.lower()

        # This PM doesn't meet the response criteria. Skip it.
        if not (usernameMention or usernameInBody):
            continue
        # Skip already tested messages
        # if message.id in readMessages:
        #     continue
        try:
            #Get comment from message
            comment = reddit.comment(message.id)
            # The default string if nothing is found
            replyString = ""
            cmt = comment.body
            originalID = comment.id
            # check if the mentioning comment has a number in it
            if comment.id not in commentsRepliedTo and comment.author not in doNotReplyList and comment.author != reddit.user.me():
                tagResultCache = getTagResultCache(cmt)
                if tagResultCache:
                    if len(tagResultCache) > 1:
                        replyString = "Why would you call the tip hotline on yourself? Anyway:\n\n" + generateReplyStringMultiple(tagResultCache)
                    else:
                        replyString = "Why would you call the tip hotline on yourself? Anyway:\n\n" + generateReplyStringSingle(tagResultCache)
                    # post a reply if numbers are found
                    if replyString:
                        writeCommentReply(replyString, comment)
                        commentsRepliedTo.append(comment.id)    
                        message.mark_read()
                        continue
                # if the tagResult is empty move on to checking the parent
                else:
                    parent = comment.parent_id
                    commentParent = re.findall(r'(?<=t1_).*', parent)
                    # postParent = re.search(r'(?<=t3_).*', parent)
                    user = comment.author
                    if commentParent:
                        comment = reddit.comment(commentParent[0])
                        cmt = comment.body
                        if comment.id not in commentsRepliedTo and comment.author not in doNotReplyList and comment.author != reddit.user.me():
                            tagResultCache = getTagResultCache(cmt)
                            if tagResultCache:
                                if len(tagResultCache) > 1:
                                    replyString = "Thanks for the tip /u/" + str(user) + ":\n\n" + generateReplyStringMultiple(tagResultCache)
                                else:
                                    replyString = "Thanks for the tip /u/" + str(user) + ":\n\n" + generateReplyStringSingle(tagResultCache)
                                if replyString:        
                                    writeCommentReply(replyString, comment)
                                    commentsRepliedTo.append(comment.id)
                                    message.mark_read()
                                    continue

                # Check if a reply was generated
                replyString = "It doesn't look like anything to me"
                comment = reddit.comment(originalID)
                if replyString:
                    # post the string and save the replied to comment to not analyse and reply again
                    # print("PrePost" + replyString)               
                    writeCommentReply(replyString, comment)
                    commentsRepliedTo.append(comment.id)
                    message.mark_read()
        except:
            break

    # Sleep for 30 seconds...
    print("Sleeping for 30 seconds...")
    time.sleep(30)


def writeCommentReply(replyString, comment):
    print("Commenting with: \n")
    print(replyString)
    # post the replyString to reddit as a reply
    reply = comment.reply(replyString)
    # also write it to file to enable reloading after shutdown
    with open("commentsRepliedTo.txt", "a") as f:
        f.write(comment.id + "\n")
    # wait after commenting to prevent cooldown from erroring out the script
    # enable if needed
    # print("Waiting for comment cooldown...")
    # time.sleep(660)
    # save the replied to comment to not analyse and reply again
    return reply


def getTagResultCache(cmt):
    tagResultCache = []
    print(cmt)
    numbers = getNumbers(cmt)
    # checks if the list is empty
    if numbers:
        print("Numbers available")
        print(numbers)
        # iterates over the list
        for number in numbers:
            print(number)
            # get the tags from the nHentai API function
            tagResult = retrieveTags(number)
            # checks if there is a full list and if it is loli
            if tagResult:
                auxiliaryTags = tagResult[0]
                if auxiliaryTags[0]:
                    tagResultCache.append([number, tagResult])
    return tagResultCache


def getNumbers(cmt):
    # find and replace with nothing to elimnate URLs from the string.
    if not re.findall(r'https?:\/\/(?:www.)?nhentai.net', cmt):
        cmt = re.sub(r'https?:\/\/\S+', '', cmt)
    # remove decimal numbers to prevent them from being parsed
    cmt = re.sub(r'\d+\.\d+', '', cmt)
    # remove numbers the nHentaiTagBot is looking for
    cmt = re.sub(r'(?<=\()\d{5,6}(?=\))', '', cmt)
    cmt = re.sub(r'(?<=\))\d{5}(?=\()', '', cmt)
    # improved parser that'll hopefully not catch anything with less than 4 digits and spaced digits.
    numbers = getNumbersFromString(cmt)
    # if the standard search doesn't find anything do a special search
    if not numbers:
        # removes all characters that aren't numbers to find raised numbers.
        commentString2 = re.sub(r'\D*\^', '', cmt)
        # then looks if they are 5 or 6 characters long.
        numbers = getNumbersFromString(commentString2)
    # if there are still no numbers found try erasing crossed out numbers
    if not numbers:
        commentString2 = re.sub(r'~~\d*~~', '', cmt)
        numbers = getNumbersFromString(commentString2)
        # numbers = re.findall(r'\b\d\s*\d\s*\d\s*\d\s*\d\s*\d?\b', commentString2)
    # use a try and catch to prevent crashing when unexpected characters get into the numbers list.
    try:
        numbers = [int(number.replace(" ", "").replace("\xa0", "").replace("\n", "")) for number in numbers]
    except ValueError:
        print("Invalid number found")
        with open("errorCollection.txt", "a") as f:
            f.write("getTagResultCache failed number parsing at " + str(datetime.datetime.now().time()) + " with: " + str(numbers) + " original comment: "+ cmt +"end\n")
    numbers = removeDuplicates(numbers)
    return numbers

def getNumbersFromString(cmt):
    numbers = re.findall(r'(?<![\/=\d\w-])\d\s*\d\s*\d\s*\d\s*\d\s*\d?\b', cmt)
    return numbers


def generateReplyStringSingle(tagResultCache):
    replyString = ""
    # uses the tagResultCache because it occurred to me that it would always use the last number not the right number if there a multiple tags but not multiple loli tags
    # uses loop because otherwise it doesn't do two in the list
    for result in tagResultCache:
        #check if list is populated
        if result:
            tagResult = result[1]
            number = result[0]
            auxiliaryTags = tagResult[0]
            # auxillary tags locations
            # use 0,1,2 to pad additionalstringstag
            loli = 0
            dickGirlOnMale = 1
            maleOnDickGirl = 2
            soleFemale = 3
            soleDickGirl = 4
            hitler = 5
            # normal tags
            english = 2
            mindBreak = 3
            rape = 4
            oppaiLoli = 5
            uglyBastard = 6
            snuff = 7
            shota = 8
            guro = 9
            scat = 10
            femdom = 11
            pregnant = 12
            inflation = 13
            futa = 14
            nonH = 15
            urination = 16
            yuri = 17
            ryona = 18
            asphyxiation = 19
            # makes a special reply based on a specific number
            if number == 215600:
                replyString += ">" + str(number) + "\n\n"
                replyString += ">Tags: Loli\n\n"
                replyString += "FBI OP-\n\n"
                replyString += ">Title: Loli in a Box\n\n"
                replyString += "Abandon hope all ye who enter here"
            elif number == 228922:
                replyString += ">" + str(number) + "\n\n"
                replyString += ">Tags: Loli\n\n"
                replyString += "FBI OPEN UP!\n\n"
                replyString += ">Tags: snuff" + getAdditionalTags(tagResult, [snuff]) + " also not english\n\n"
                replyString += "...I come into a region where is nothing that can give light.\n\n"
            elif number == 238212:
                replyString += ">" + str(number) + "\n\n"
                replyString += ">Tags: Loli\n\n"
                replyString += "FBI OPEN UP!\n\n"
                replyString += ">Tags: guro" + getAdditionalTags(tagResult, [guro]) + "\n\n"
                replyString += "There they blaspheme the puissance divine.\n\n"
                replyString += "I understood that unto such a torment the carnal malefactors were condemned."
            else:
                # write response based on returned results uses multiple lines for readability
                if number == 17703:
                    replyString += "Did you perchance mean 1770**1**3 for some good, clean, non-loli fun?\n\n"
                    replyString += "But I got to do my job so...\n\n"
                elif number == 56709:
                    #Awoo telephone song
                    replyString += "So you think that you can get away with coding the numbers in a song?\n\n"
                    replyString += "Wrong! Stop right here criminal scum!\n\n"
                elif number == 25252:
                    replyString += "Looks like I'll have to bust some Nico Nico Niicaps, although... \n\n"
                # Starts all comments off the same
                # pad number with leading zeroes if smaller than 5 digits.
                if number >= 10000:
                    replyString += ">" + str(number) + "\n\n"
                else:
                    replyString += ">" + str(number).zfill(5) + "\n\n"
                replyString += ">Tags: Loli\n\n"
                # Depending on the returned results different endings are appended
                if auxiliaryTags[hitler]:
                    replyString += "GESTAPO ÖFFNEN SIE DIE TÜR! \n\n"
                    replyString += ">Character: Adolf Hitler + tags: " + getAllTags(tagResult) + "\n\n"
                    replyString += "Nein, mein Führer! \n\n"
                    replyString += "I would do anything for Germany, but I can't let you do that."
                elif tagResult[mindBreak]:
                    replyString += "FBI OPEN-\n\n"
                    replyString += ">Tags: mind break" + getAdditionalTags(tagResult, [mindBreak]) + "\n\n"
                    replyString += "Two nukes weren't enough\n\n"
                elif tagResult[femdom] and tagResult[rape]:
                    replyString += "KGB OPEN UP!\n\n"
                    replyString += ">Tags: femdom + rape" + getAdditionalTags(tagResult, [femdom, rape]) + "\n\n"
                    replyString += "In Soviet Russia Loli rapes you!\n\n"
                elif tagResult[rape]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: rape" + getAdditionalTags(tagResult, [rape]) + "\n\n"
                    replyString += "Calling the Loli Special Victims Unit\n\n"
                    if tagResult[snuff]:
                        replyString += "Wait... \n\n"
                        replyString += ">Tags: **snuff**\n\n"
                        replyString += "Scratch that dispatch, we're going to need the coroner\n\n"
                elif tagResult[uglyBastard]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: ugly bastard" + getAdditionalTags(tagResult, [uglyBastard]) + "\n\n"
                    replyString += "**gunshot**\n\n"
                    replyString += "That sick bastard had to be put down.\n\n"
                elif tagResult[snuff]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: snuff" + getAdditionalTags(tagResult, [snuff]) + "\n\n"
                    replyString += "*The lolice officer tried to enter but the stench of decay drove him back.*\n\n"
                elif tagResult[guro]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: guro" + getAdditionalTags(tagResult, [guro]) + "\n\n"
                    replyString += "Oh god, there is blood everywhere!\n\n"
                elif tagResult[ryona]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: ryona" + getAdditionalTags(tagResult, [guro]) + "\n\n"
                    replyString += "**grabs nightstick**\n\n"
                    replyString += "Allright boys, let's give them a taste of their own medicine!"
                elif tagResult[scat]:
                    replyString += "FBI OPEN UP!!\n\n"
                    replyString += ">Tags: scat" + getAdditionalTags(tagResult, [scat]) + "\n\n"
                    replyString += "That smell. A kind of smelly smell. The smelly smell that smells... smelly.\n\n"
                elif tagResult[oppaiLoli]:
                    replyString += "FBI ...wait a minute...\n\n"
                    replyString += ">Tags: Oppai Loli" + getAdditionalTags(tagResult, [oppaiLoli]) + "\n\n"
                    replyString += "Loli. You keep using that word, I do not think it means what you think it means\n\n"
                elif tagResult[futa]:
                    replyString += "FBI OPEN UP!\n\n"
                    if auxiliaryTags[dickGirlOnMale]:
                        replyString += ">Tags: futa + dickgirl on male" + getAdditionalTags(tagResult, [futa, 0]) + "\n\n"
                        replyString += "Wait, isn't this just homosexuality with extra steps?\n\n"
                    elif auxiliaryTags[maleOnDickGirl]:
                        replyString += ">Tags: futa + male on dickgirl" + getAdditionalTags(tagResult, [futa, 0]) + "\n\n"
                        replyString += "That's not how this works. That's not how any of this works.\n\n"
                    elif auxiliaryTags[soleFemale] and auxiliaryTags[soleDickGirl]:
                        replyString += ">Tags: futa + sole female + sole dickgirl" + getAdditionalTags(tagResult, [futa, 0, 1]) + "\n\n"
                        replyString += "Whatever, let's just book the one with the penis.\n\n"
                    else:
                        replyString += ">Tags: futa" + getAdditionalTags(tagResult, [futa]) + "\n\n"
                        replyString += "Chicks with dicks? Nope, I'm out!\n\n"
                elif tagResult[femdom]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: femdom" + getAdditionalTags(tagResult, [femdom]) + "\n\n"
                    replyString += "NO! Get your tiny hand off of my belt buckle!\n\n"
                    replyString += "We might have to go easy on the guy 'cause this girl is a go getter.\n\n"
                elif tagResult[shota]:
                    replyString += "FBI OPEN UP!!\n\n"
                    replyString += ">Tags: shota" + getAdditionalTags(tagResult, [shota]) + "\n\n"
                    replyString += "Wait, is this just kids doing each other!?\n\n"
                elif tagResult[pregnant]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: pregnant" + getAdditionalTags(tagResult, [pregnant]) + "\n\n"
                    replyString += "WTF, this is sick. Kids shouldn't be having kids.\n\n"
                elif tagResult[inflation]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: inflation" + getAdditionalTags(tagResult, [inflation]) + "\n\n"
                    replyString += "Lolis aren't balloons, you can't just inflate them!\n\n"
                elif tagResult[urination]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: urination" + getAdditionalTags(tagResult, [urination]) + "\n\n"
                    replyString += "I'm sorry Mr. President, lolis aren't for golden showers."
                elif tagResult[asphyxiation]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: asphyxiation" + getAdditionalTags(tagResult, [asphyxiation]) + "\n\n"
                    replyString += "Someone get me an oxygen mask stat!"
                elif tagResult[yuri]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: yuri" + getAdditionalTags(tagResult, [yuri]) + "\n\n"
                    replyString += "Uh, sorry for the intrusion ladies. Carry on but try to keep it down.\n\n"
                    if not tagResult[english]:
                        replyString += ">Language: Not English\n\n"
                        replyString += "I'll never forgive the Japanese!"
                # Should be at the end since it won't be wholesome otherwise.
                elif tagResult[nonH]:
                    replyString += "FBI OPEN UP!\n\n"
                    replyString += ">Tags: non-H" + getAdditionalTags(tagResult, [nonH]) + "\n\n"
                    replyString += "Wait a minute, non-H? Are these the wholesome headpats I've heard rumors of? Sorry about the door, carry on citizen.\n\n"
                    if not tagResult[english]:
                        replyString += "I still don't know how to read moon runes though.\n\n"
                elif tagResult[1] > 15:
                    replyString += ">" + getAdditionalTags(tagResult, []) + "\n\n"
                    replyString += "Oh, I have a bad feeling about this\n\n"
                else:
                    replyString += "FBI OPEN UP!\n\n"
                # Add english check at the end. Ignore non-H since it doesn't fit
                if not tagResult[english] and not (tagResult[nonH] or tagResult[yuri]):
                    replyString += ">Language: Not English\n\n"
                    replyString += "Do I look like I can read moon runes? It doesn't matter what's legal on the moon, but here in 'murica we protect the lolis. Put him away boys!\n\n"
    return replyString


def getAdditionalTags(tagResult, AlreadyUsedNumbers):
    currentPosition = 0
    numberOfTrueTags = 1
    replyString = ""
    firstTag = True
    for number in AlreadyUsedNumbers:
        numberOfTrueTags += 1
    for tag in tagResult:
        if currentPosition > 2 and tag and currentPosition not in AlreadyUsedNumbers:
            replyString += ", " + stringsToTags[currentPosition]
            numberOfTrueTags += 1
            firstTag = False
        currentPosition += 1
    if firstTag and not AlreadyUsedNumbers:
        replyString += str(tagResult[1]-numberOfTrueTags) + " other tags"
    else:
        replyString += ", and " + str(tagResult[1]-numberOfTrueTags) + " other tags"
    return replyString


def getAllTags(tagResult):
    currentPosition = 0
    currentPosition = 0
    found = False
    replyString = ""
    for tag in tagResult:
        if tag and currentPosition > 2:
            found = True
            break
        currentPosition += 1
    if found:
        replyString = stringsToTags[currentPosition] + getAdditionalTags(tagResult, [currentPosition])
    return replyString


def generateReplyStringMultiple(tagResultCache):
    replyString = ""
    # grab the indiviual lists
    for result in tagResultCache:
        # check if the list is populated
        if result:
            positionCounter = 0
            # assign the variables based on the stored parts
            tagResult = result[1]
            # print(tagResult)
            number = result[0]
            # check if there is an actual tagResult stored
            if tagResult:
                # fill the reply based on the rules like below
                # All found start off the same.
                if number >= 10000:
                    replyString += ">" + str(number) + "\n\n"
                else:
                    replyString += ">" + str(number).zfill(5) + "\n\n"
                replyString += ">>Tags: Loli"
                # Start at one because it'll always be loli
                numberOfTrueTags = 1
                # loop always starts at 0
                positionCounter = 0
                # iterate through tags
                for tag in tagResult:
                    # first three positions are loli, tag count and english, so they need to be skipped.
                    if positionCounter > 2:
                        # check for tag presense and if it is first tag
                        if tag:
                            # Start the second line and grab the string from the list
                            replyString += ", " + stringsToTags[positionCounter]
                            numberOfTrueTags += 1
                    # adjust the counter for the next loop
                    positionCounter += 1
                # the additional tags at the end logic
                replyString += ", and " + str(tagResult[1]-numberOfTrueTags) + " other tags"
                if not tagResult[2]:
                    replyString += " also not english"
                replyString += "\n\n"
    # add an ending depending on the number of tags
    if len(tagResultCache) < 3:
        replyString += "I sure hope this isn't the humble beginning of some grand collection."
    elif len(tagResultCache) < 6:
        replyString += "Are you Jared from Subway?"
    else:
        replyString += "We are going to need a bigger van for this raid..."
    return replyString


def retrieveTags(galleryNumber):
    # checks if the number is close to the current max to prevent using astronomical numbers
    if galleryNumber < 300000:
        # make galleryNumber a String for concat
        galleryNumber = str(galleryNumber)
        # nhentaiTags = requests.get(API_URL+galleryNumber).json() # ['tags'] #
        request = requests.get(API_URL + str(galleryNumber))
        # catch erounious requests
        if request.status_code != 200:
            return []
        nhentaiTags = json.loads(re.search(r'(?<=N.gallery\().*(?=\))', request.text).group(0))
        # catch returns for invalid numbers
        if "error" in nhentaiTags:
            return []
        else:
            # define a couple of variables
            isLoli = False
            numberOfTags = 0
            isEnglish = False
            isMindBreak = False
            isRape = False
            isOppaiLoli = False
            isUglyBastard = False
            isSnuff = False
            isShota = False
            isGuro = False
            isScat = False
            isFemdom = False
            isPregnant = False
            isInflation = False
            isFuta = False
            isNonH = False
            isUrination = False
            isYuri = False
            isRyona = False
            isAsphyxiation = False
            isSoleFemale = False
            isSoleDickGirl = False
            isDickGirlOnMale = False
            isMaleOnDickGirl = False
            isHitler = False
            # iterates over the parts of tags inspired by https://stackoverflow.com/questions/6386308/http-requests-and-json-parsing-in-python
            for tags in nhentaiTags['tags']:
                # count the number of tags actually labled with tag
                if 'tag' in tags['type']:
                    numberOfTags += 1
                # checks for loli
                if 'lolicon' in tags['name']:
                    isLoli = True
                # checks for mind break
                elif "mind break" in tags['name']:
                    isMindBreak = True
                elif 'rape' in tags['name']:
                    isRape = True
                elif "oppai loli" in tags['name']:
                    isOppaiLoli = True
                elif 'bbm' in tags['name']:
                    isUglyBastard = True
                elif 'snuff' in tags['name']:
                    isSnuff = True
                elif 'shotacon' in tags['name']:
                    isShota = True
                elif 'guro' in tags['name']:
                    isGuro = True
                elif 'scat' in tags['name']:
                    isScat = True
                elif 'english' in tags['name']:
                    isEnglish = True
                elif 'femdom' in tags['name']:
                    isFemdom = True
                elif 'pregnant' in tags['name']:
                    isPregnant = True
                elif 'inflation' in tags['name']:
                    isInflation = True
                elif 'futanari' in tags['name']:
                    isFuta = True
                elif 'non-h' in tags['name']:
                    isNonH = True
                elif 'urination' in tags['name']:
                    isUrination = True
                elif 'yuri' in tags['name']:
                    isYuri = True
                elif 'ryona' in tags['name']:
                    isRyona = True
                elif 'asphyxiation' in tags['name']:
                    isAsphyxiation = True
                # auxiliary tags
                elif "dickgirl on male" in tags['name']:
                    isDickGirlOnMale = True
                elif "male on dickgirl" in tags['name']:
                    isMaleOnDickGirl = True
                elif "sole female" in tags['name']:
                    isSoleFemale = True
                elif "sole dickgirl" in tags['name']:
                    isSoleDickGirl = True
                elif "adolf hitler" in tags['name']:
                    isHitler = True
            # returns all values
            # potentially replace isLoli with colleteral tags and adjust the check in tagscollection and other (unessesary) checks
            auxiliaryTags = [isLoli, isDickGirlOnMale, isMaleOnDickGirl, isSoleFemale, isSoleDickGirl, isHitler]
            return [auxiliaryTags, numberOfTags, isEnglish ,isMindBreak, isRape, isOppaiLoli, isUglyBastard, isSnuff, isShota, isGuro, isScat, isFemdom, isPregnant, isInflation, isFuta, isNonH, isUrination, isYuri, isRyona, isAsphyxiation]


# load the already replied to comments from the file
def getSavedComments():
    # return an empty list if empty
    if not os.path.isfile("commentsRepliedTo.txt"):
        commentsRepliedTo = []
    else:
        with open("commentsRepliedTo.txt", "r") as f:
            # updated read file method from https://stackoverflow.com/questions/3925614/how-do-you-read-a-file-into-a-list-in-python
            commentsRepliedTo = f.read().splitlines()

    return commentsRepliedTo


def getSavedPosts():
    # return an empty list if empty
    if not os.path.isfile("postsRepliedTo.txt"):
        postsRepliedTo = []
    else:
        with open("postsRepliedTo.txt", "r") as f:
            # updated read file method from https://stackoverflow.com/questions/3925614/how-do-you-read-a-file-into-a-list-in-python
            postsRepliedTo = f.read().splitlines()

    return postsRepliedTo


# taken from https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order
def removeDuplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


# followed the recommendation of Bryce Boe and made this bot importable
if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            pass
    # main()