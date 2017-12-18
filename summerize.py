from collections import Counter
from math import fabs
from re import split as regex_split, sub as regex_sub, UNICODE as REGEX_UNICODE

stopWords = set([
    "-", " ", ",", ".", "a", "e", "i", "o", "u", "t", "about", "above",
    "above", "across", "after", "afterwards", "again", "against", "all",
    "almost", "alone", "along", "already", "also", "although", "always",
    "am", "among", "amongst", "amoungst", "amount", "an", "and",
    "another", "any", "anyhow", "anyone", "anything", "anyway",
    "anywhere", "are", "around", "as", "at", "back", "be", "became",
    "because", "become", "becomes", "becoming", "been", "before",
    "beforehand", "behind", "being", "below", "beside", "besides",
    "between", "beyond", "both", "bottom", "but", "by", "call", "can",
    "cannot", "can't", "co", "con", "could", "couldn't", "de",
    "describe", "detail", "did", "do", "done", "down", "due", "during",
    "each", "eg", "eight", "either", "eleven", "else", "elsewhere",
    "empty", "enough", "etc", "even", "ever", "every", "everyone",
    "everything", "everywhere", "except", "few", "fifteen", "fifty",
    "fill", "find", "fire", "first", "five", "for", "former",
    "formerly", "forty", "found", "four", "from", "front", "full",
    "further", "get", "give", "go", "got", "had", "has", "hasnt",
    "have", "he", "hence", "her", "here", "hereafter", "hereby",
    "herein", "hereupon", "hers", "herself", "him", "himself", "his",
    "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
    "into", "is", "it", "its", "it's", "itself", "just", "keep", "last",
    "latter", "latterly", "least", "less", "like", "ltd", "made", "make",
    "many", "may", "me", "meanwhile", "might", "mill", "mine", "more",
    "moreover", "most", "mostly", "move", "much", "must", "my", "myself",
    "name", "namely", "neither", "never", "nevertheless", "new", "next",
    "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing",
    "now", "nowhere", "of", "off", "often", "on", "once", "one", "only",
    "onto", "or", "other", "others", "otherwise", "our", "ours",
    "ourselves", "out", "over", "own", "part", "people", "per",
    "perhaps", "please", "put", "rather", "re", "said", "same", "see",
    "seem", "seemed", "seeming", "seems", "several", "she", "should",
    "show", "side", "since", "sincere", "six", "sixty", "so", "some",
    "somehow", "someone", "something", "sometime", "sometimes",
    "somewhere", "still", "such", "take", "ten", "than", "that", "the",
    "their", "them", "themselves", "then", "thence", "there",
    "thereafter", "thereby", "therefore", "therein", "thereupon",
    "these", "they", "thickv", "thin", "third", "this", "those",
    "though", "three", "through", "throughout", "thru", "thus", "to",
    "together", "too", "top", "toward", "towards", "twelve", "twenty",
    "two", "un", "under", "until", "up", "upon", "us", "use", "very",
    "via", "want", "was", "we", "well", "were", "what", "whatever",
    "when", "whence", "whenever", "where", "whereafter", "whereas",
    "whereby", "wherein", "whereupon", "wherever", "whether", "which",
    "while", "whither", "who", "whoever", "whole", "whom", "whose",
    "why", "will", "with", "within", "without", "would", "yet", "you",
    "your", "yours", "yourself", "yourselves", "the", "reuters", "news",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
    "sunday", "mon", "tue", "wed", "thu", "fri", "sat", "sun",
    "rappler", "rapplercom", "inquirer", "yahoo", "home", "sports",
    "1", "10", "2012", "sa", "says", "tweet", "pm", "home", "homepage",
    "sports", "section", "newsinfo", "stories", "story", "photo",
    "2013", "na", "ng", "ang", "year", "years", "percent", "ko", "ako",
    "yung", "yun", "2", "3", "4", "5", "6", "7", "8", "9", "0", "time",
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
    "government", "police"
])
ideal = 20.0


def SummarizeUrl(url):
    summaries = []
    try:
        article = grab_link(url)
    except IOError:
        print 'IOError'
        return None

    if not (article and article.cleaned_text and article.title):
        return None
    print article.title
    print article.cleaned_text
    summaries = Summarize(unicode(article.title),
                          unicode(article.cleaned_text))
    return summaries
    


def Summarize(title, text):
    summaries = []
    sentences = split_sentences(text)
    keys = keywords(text)
    titleWords = split_words(title)

    if len(sentences) <= 5:
        return sentences

    #score setences, and use the top 5 sentences
    ranks = score(sentences, titleWords, keys).most_common(3)
    for rank in ranks:
        summaries.append(rank[0])

    return summaries


def grab_link(inurl):
    #extract article information using Python Goose
    from goose import Goose
    try:
        article = Goose().extract(url=inurl)
	print article
        return article
    except ValueError:
        print 'Goose failed to extract article from url'
        return None
    return None


def score(sentences, titleWords, keywords):
    #score sentences based on different features

    senSize = len(sentences)
    ranks = Counter()
    for i, s in enumerate(sentences):
        sentence = split_words(s)
        titleFeature = title_score(titleWords, sentence)
        sentenceLength = length_score(sentence)
        sentencePosition = sentence_position(i+1, senSize)
        sbsFeature = sbs(sentence, keywords)
        dbsFeature = dbs(sentence, keywords)
        frequency = (sbsFeature + dbsFeature) / 2.0 * 10.0

        #weighted average of scores from four categories
        totalScore = (titleFeature*1.5 + frequency*2.0 +
                      sentenceLength*1.0 + sentencePosition*1.0) / 4.0
        ranks[s] = totalScore
    return ranks


def sbs(words, keywords):
    score = 0.0
    if len(words) == 0:
        return 0
    for word in words:
        if word in keywords:
            score += keywords[word]
    return (1.0 / fabs(len(words)) * score)/10.0


def dbs(words, keywords):
    if (len(words) == 0):
        return 0

    summ = 0
    first = []
    second = []

    for i, word in enumerate(words):
        if word in keywords:
            score = keywords[word]
            if first == []:
                first = [i, score]
            else:
                second = first
                first = [i, score]
                dif = first[0] - second[0]
                summ += (first[1]*second[1]) / (dif ** 2)

    # number of intersections
    k = len(set(keywords.keys()).intersection(set(words))) + 1
    return (1/(k*(k+1.0))*summ)


def split_words(text):
    #split a string into array of words
    try:
        text = regex_sub(r'[^\w ]', '', text, flags=REGEX_UNICODE)  # strip special chars
        return [x.strip('.').lower() for x in text.split()]
    except TypeError:
        print "Error while splitting characters"
        return None


def keywords(text):
    """get the top 10 keywords and their frequency scores
    ignores blacklisted words in stopWords,
    counts the number of occurrences of each word
    """
    text = split_words(text)
    numWords = len(text)  # of words before removing blacklist words
    freq = Counter(x for x in text if x not in stopWords)

    minSize = min(10, len(freq))  # get first 10
    keywords = {x: y for x, y in freq.most_common(minSize)}  # recreate a dict

    for k in keywords:
        articleScore = keywords[k]*1.0 / numWords
        keywords[k] = articleScore * 1.5 + 1

    return keywords


def split_sentences(text):
    '''
    The regular expression matches all sentence ending punctuation and splits the string at those points.
    At this point in the code, the list looks like this ["Hello, world", "!" ... ]. The punctuation and all quotation marks
    are separated from the actual text. The first s_iter line turns each group of two items in the list into a tuple,
    excluding the last item in the list (the last item in the list does not need to have this performed on it). Then,
    the second s_iter line combines each tuple in the list into a single item and removes any whitespace at the beginning
    of the line. Now, the s_iter list is formatted correctly but it is missing the last item of the sentences list. The
    second to last line adds this item to the s_iter list and the last line returns the full list.
    '''
    
    sentences = regex_split(u'(?<![A-ZА-ЯЁ])([.!?]"?)(?=\s+\"?[A-ZА-ЯЁ])', text, flags=REGEX_UNICODE)
    s_iter = zip(*[iter(sentences[:-1])] * 2)
    s_iter = [''.join(map(unicode,y)).lstrip() for y in s_iter]
    s_iter.append(sentences[-1])
    return s_iter



def length_score(sentence):
    return 1 - fabs(ideal - len(sentence)) / ideal


def title_score(title, sentence):
    title = [x for x in title if x not in stopWords]
    count = 0.0
    for word in sentence:
        if (word not in stopWords and word in title):
            count += 1.0
            
    if len(title) == 0:
        return 0.0
        
    return count/len(title)


def sentence_position(i, size):
    """different sentence positions indicate different
    probability of being an important sentence"""

    normalized = i*1.0 / size
    if 0 < normalized <= 0.1:
        return 0.17
    elif 0.1 < normalized <= 0.2:
        return 0.23
    elif 0.2 < normalized <= 0.3:
        return 0.14
    elif 0.3 < normalized <= 0.4:
        return 0.08
    elif 0.4 < normalized <= 0.5:
        return 0.05
    elif 0.5 < normalized <= 0.6:
        return 0.04
    elif 0.6 < normalized <= 0.7:
        return 0.06
    elif 0.7 < normalized <= 0.8:
        return 0.04
    elif 0.8 < normalized <= 0.9:
        return 0.04
    elif 0.9 < normalized <= 1.0:
        return 0.15
    else:
        return 0


url = 'https://www.outlookindia.com/website/story/delhi-hc-refuses-to-restrain-arnab-goswami-republic-tv-from-airing-news-about-su/305034?utm_campaign=awesummly&utm_source=awesummly'
#Uncommment this to use url as data set.
#y = SummarizeUrl(url)
y = Summarize("HC refuses to stop Goswami from reporting on Pushkar's death","The Delhi High Court on Friday refused to restrain journalist Arnab Goswami and his Republic TV from airing news about Congress MP Shashi Tharoor's wife Sunanda Pushkar's death case. The High Court also said that the press has to exercise care and caution while reporting about matters under investigation or pending trial, the Live Law reported. Every individual has a right to silence. He cannot be forced or compelled to speak on the issue, Justice Manmohan said. The court's order came on three different applications filed by Tharoor in his Rs 2 crore defamation suit against Goswami and the channel for allegedly making defamatory remarks against him while airing news relating to the mysterious death of his wife. Earlier in September, the Delhi High Court refrained from passing any interim order restraining Goswami and his news channel from airing any news or debate in connection with Pushkar's death case. Justice Manmohan had issued notice to Goswami and sought their responses on Tharoor's plea to restrain them from allegedly misreporting the contents of court proceedings related to Pushkar's death. It had also observed that the Congress leader has not shown any law by which investigation cannot be done by the journalist. Show me that after the first date of hearing, he (Goswami) has called you a murderer, the judge said, adding I cannot dictate what should be the editorial policy of a news channel. The Congress leader has alleged that after the last date of hearing on August 16, the journalist and his channel continued to indulge in misreporting and had broadcast an 8-hour programme on September 4 related to his wife's death. Sunanda Pushkar was found dead at a suite in a five star hotel in South Delhi on the night of January 17, 2014. Tharoor said the said channel's broadcast was a bid to establish itself. The media has very important role as a witness but the media doesn't have a role of being a prosecutor, a judge or an executioner. The Thiruvananthapuram MP said he had nothing to hide and had been fully cooperative with the police. Earlier this year, the head of All India Institutes of Medical Sciences (AIIMS) forensic department, Sudhir Gupta had confirmed that the death of Sunanda Pushkar Tharoor was unnatural and caused due to poisoning. We clearly said that this is a case of poisoning. This has been clearly stated in the opinion. This opinion has been made and formed on the basis of circumstantial evidence where certain drugs and poison have been recovered by Delhi police itself, Gupta told ANI.")
print ' '.join(y)

