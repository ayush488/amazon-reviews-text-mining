import urllib2
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from collections import defaultdict

def ngrams(words, n=2):
    """
    This method returns a list of phrases, with "n" words per phrase.
    Eg. "The quick brown fox jumps over the lazy dog." when passed to this 
    method with n = 3 returns:
    ['the quick brown', 'quick brown fox', 'brown fox jumps', 'fox jumps over',
    'jumps over the', 'over the lazy', 'the lazy dog.']
    """
    grams = [" ".join(words[x:x+n]) for x in xrange(len(words)-n+1)]
    return grams

def get_reviews(prod_id, no_of_pages, country="in"):
    """
    Method to get reviews about a product from Amazon based on the product ID.
    Receives an argument "no_of_pages" to determine how many pages of reviews
    must be retrieved (A standard page has 10 reviews on it).
    Returns a list of all reviews retrieved.
    """

    reviews = []

    for page in range(no_of_pages):
        print "Fetching page", (page+1)
        url=("http://www.amazon.{0}/product-reviews/{1}" +
             "/ref=cm_cr_getr_d_paging_btm_{2}?pageNumber={2}")
        url = url.format(country, prod_id, page+1)

        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page, "lxml")
        page_reviews = soup.find_all("span", class_="a-size-base review-text")
        reviews.extend([rev.text for rev in page_reviews])

    return reviews

def token_frequency(reviews_list, grams):
    """
    Calculates the count of all unique tokens from all the reviews retrieved
    from Amazon, and stores them as "word : count" pairs.
    We remove all stopwords, i.e. frequently occuring words such as articles,
    and prepositions as they do not hold much value.
    """

    all_words = defaultdict(int)
    reviews_string = " ".join(reviews_list)

    # Delete non-alphanumeric chars
    useful_words = re.split(r'[^0-9A-Za-z]+',reviews_string)
    useful_words = ngrams(useful_words, grams)
    for word in useful_words:
        all_words[word.lower()] += 1

    #Stop-words will not be detected if grams > 1, i.e more than one word per
    # phrase. A work-around for this would be to search and delete stop-words
    # before calling the ngrams() function, but considering useful_words is a
    # list, that would be inefficient.

    stop_words = set(stopwords.words('english'))
    # Compute this only if grams = 1, no effect if grams > 1
    if grams ==1:
        for key, val in all_words.items():
            if key in stop_words:
                del all_words[key]
    
    return all_words

def plot_frequency(words, limit):
    """
    Sorts the all_words dictionary in descending order based on the value
    (count) of occurence of a word. The "limit" argument is a measure of the
    top "limit" words we are interested in.
    Finally, the most frequently occuring words in the product's reviews are
    output on the console as a Pandas DataFrame, and also graphically plotted
    as a bar chart with matplotlib.
    From the results we can see, for instance, what feature of the product is
    most mentioned in reviews, or if competitors (Flipkart, Snapdeal, etc.)
    are mentioned in reviews, indicating comparisons by users.
    """

    top_words = []
    values = []
    sorted_dict = sorted(words, key=words.get, reverse=True)
 
    for key in sorted_dict[:limit]:
        top_words.append(key)
        values.append(words[key])

    stats = {"Word": top_words,
             "Word Count": values}

    df = pd.DataFrame(stats, index=[range(1, limit + 1)])

    pos = np.arange(len(top_words))
    ax = plt.axes()
    ax.set_xticks(pos)
    ax.set_yticks(range(0,max(values),5))
    ax.set_xticklabels(top_words, rotation='vertical', fontsize=10)
    plt.bar(pos, values, 0.6, color="c")
    plt.show()

def main():
    """
    Here we call methods, and pass the ID of the product of interest, the
    number of pages of reviews we want to obtain, and also specify how many
    words we want to know the count of.
    """
    prod_id = "B00O4WTPOC" # iPhone 6
    grams = 3  # to search for phrases with "grams" number of words
    pages = 10
    no_of_words = 25
    all_reviews = get_reviews(prod_id, pages)
    all_words = token_frequency(all_reviews, grams)
    plot_frequency(all_words, no_of_words)

if __name__ == '__main__':
    main()
