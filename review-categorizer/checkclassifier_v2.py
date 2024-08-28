# !pip install spacy
# !python -m spacy download fr_core_news_sm
# !python -m spacy download es_core_news_sm
# !python -m spacy download en_core_web_sm
# !pip install transformers
# !pip install sentencepiece

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import spacy
import requests
import json
import traceback
import nltk


def english_segmentation(text):
    """
    This function segments a given English text into sentences based on certain conditions.
    It uses the spaCy library for tokenization and part-of-speech tagging.
    """

    # Load the English language model in spaCy
    nlp = spacy.load("en_core_web_sm")

    # Process the text with spaCy
    doc = nlp(text)

    # Initialize variables
    sentences = []
    current_sentence = []
    word_count = 0

    # Lists of exceptions and included tokens
    excepted_tokens = {"AND", "ET", "THAT"}
    included_tokens = {"|", "."}

    # Iterate over each token in the processed text
    for token in doc:
        # Check if the token is a sentence-ending token
        if (token.pos_ in {"CCONJ", "ADV"} and token.text.upper() not in excepted_tokens) or (token.text in included_tokens):
            # Process the current sentence
            process_sentence(current_sentence, word_count, sentences, token)
        else:
            # Add the token to the current sentence
            current_sentence.append(token.text)
            word_count += 1

    # Process any remaining sentence
    if current_sentence:
        sentences.append(" ".join(current_sentence).strip())

    return sentences


def process_sentence(current_sentence, word_count, sentences, token):
    """
    Process the current sentence based on the token and update the sentences list.
    """
    if current_sentence:
        if (token.text in {",", "|"}) and word_count > 3:
            sentences.append(" ".join(current_sentence).strip())
            current_sentence.clear()
            word_count = 0
        elif token.text == "," and word_count <= 3:
            current_sentence.append(token.text)
            word_count += 1
        else:
            sentences.append(" ".join(current_sentence).strip())
            current_sentence.clear()
            word_count = 1
    else:
        current_sentence.append(token.text)
        word_count += 1


def spanish_segmentation(text):
    """
    This function takes a text in Spanish as input and segments it into sentences.
    It uses the spaCy library to process the text and identify sentence boundaries.
    The function considers certain parts of speech and punctuation marks to determine sentence breaks.
    """

    # Load the Spanish language model in spaCy
    nlp = spacy.load("es_core_web_sm")

    # Process the text with spaCy
    doc = nlp(text)

    # Initialize an empty string to store the current sentence and a counter for word count
    sentence = ""
    word_count = 0

    # Initialize an empty list to store the segmented sentences
    result = []

    # Iterate over each token in the processed text
    for token in doc:

        # Check if the token is a coordinating conjunction, adverb, or a pipe character
        if token.pos_ in ["CCONJ", "ADV"] or token.text == "|":

            # If the current sentence is not empty
            if sentence != "":
                # Check if the token is a comma or a pipe and the word count is greater than 3
                if (token.text == "," or token.text == "|") and word_count > 3:
                    # Add the current sentence to the result list and reset the sentence and word count
                    result.append(sentence)
                    sentence = ""
                    word_count = 0
                # If the token is a comma and the word count is less than or equal to 3
                elif token.text == "," and word_count <= 3:
                    # Add the token to the current sentence and increment the word count
                    sentence = "".join([sentence, token.text])
                    word_count += 1
                else:
                    # Add the current sentence to the result list and start a new sentence with the token
                    result.append(sentence)
                    sentence = token.text
                    word_count = 1
            else:
                # If the current sentence is empty, add the token to the sentence and increment the word count
                sentence = "".join([sentence, token.text])
                word_count += 1

        else:
            # If the token is not a coordinating conjunction, adverb, or a pipe character, add it to the current sentence and increment the word count
            sentence = " ".join([sentence, token.text])
            word_count += 1

    # If the current sentence is not empty and contains more than one word, add it to the result list
    if sentence != "" and len(sentence.split()) > 1:
        result.append(sentence.strip())

    # Return the segmented sentences, removing any empty strings


def french_segmentation(text):
    """
    This function takes a string of text in French and splits it into sentences.
    It uses the nltk library's sent_tokenize function for French text segmentation.

    Args:
    text (str): The input text to be segmented into sentences.

    Returns:
    list: A list of sentences.
    """
    # Ensure that the French tokenizer is downloaded
    nltk.download('punkt')

    # Tokenize the text into sentences
    sentences = nltk.sent_tokenize(text, language='french')

    return sentences


# This function segments text based on the language specified.
# It uses different segmentation functions for different languages.
def segment_text(text, language):
    # Define a dictionary that maps languages to their respective segmentation functions.
    segmentation_functions = {
        "en": english_segmentation,  # Function for English text segmentation.
        "fr": french_segmentation,   # Function for French text segmentation.
        "es": spanish_segmentation,  # Function for Spanish text segmentation.
    }

    # Get the segmentation function for the specified language from the dictionary.
    segmentation_function = segmentation_functions.get(language)

    # If a segmentation function is found for the specified language, use it to segment the text.
    if segmentation_function:
        return segmentation_function(text)
    # If no segmentation function is found for the specified language, raise a ValueError.
    else:
        raise ValueError(f"Unsupported language: {language}")


def classify_text(categories, text):
    # Initialize the zero-shot classification pipeline with the specified model
    # The device is set to -1 to use the CPU

    classifier = pipeline('zero-shot-classification',
                          device=-1, model='cross-encoder/nli-deberta-v3-base')

    # classifier = pipeline("zero-shot-classification", device=-1, model="facebook/bart-large-mnli")

    # Classify the text using the provided categories
    # The multi_labels parameter is set to True to allow multiple categories for a single text
    result = classifier(text, categories, multi_labels=True)

    # Return the result of the classification
    return result


# This function analyzes a text review and categorizes it based on a set of labels.
def analyse_text(review_item, labels, entity='review', min_score=0.8, language='fr'):

    # This nested function filters out labels that have a score less than the minimum score.
    def filter_labels(prediction, min_score=0.8):
        return [(label, score) for label, score in zip(prediction['labels'], prediction['scores']) if score >= min_score]

    # This nested function returns the label with the highest score.
    def max_label(prediction):
        if not prediction['labels']:
            return None
        return max(zip(prediction['labels'], prediction['scores']), key=lambda x: x[1])

    # This nested function formats the results into a specific format.
    def format_results(results, review, entity, categories):
        def format_line(line, review, entity, categories):
            obj = {
                "section": line[0],
                "category": line[1][0],
                "confidence": line[1][1],
                "checked": categories,
                "review": "",
                "socialPost": "",
                "socialComment": ""
            }
            obj[entity] = str(review["id"])
            return obj

        return [format_line(x, review, entity, categories) for x in results]

    # This nested function analyzes a sentence and returns the results.
    def sentence_analyse(sentence, entity='review'):
        words = sentence.split()
        current_sentence = ""
        last_sentence = ""
        last_category = None
        results = []

        # Iterate over each word in the list of words
        for word in words:
            # Add the current word to the current sentence
            current_sentence += word + " "

            # Classify the current sentence and filter out labels with a score below the minimum score
            categories = filter_labels(classify_text(
                labels, current_sentence.strip()), min_score)

            # If there are no previous categories and there are categories for the current sentence,
            # set the last category to the first category of the current sentence
            if not last_category and categories:
                last_category = categories[0]

            # If there are categories for the current sentence and the first category is different from the last category,
            # append the last sentence and its category to the results list, update the last category to the first category of the current sentence,
            # and reset the current sentence to the current word
            elif categories and categories[0][0] != last_category[0]:
                results.append((last_sentence.strip(), last_category))
                last_category = categories[0]
                current_sentence = word + " "

            # If the categories for the current sentence are the same as the last category,
            # update the last sentence to the current sentence
            else:
                last_sentence = current_sentence

        # If there is a last sentence and a last category, append the current sentence and its category to the results list
        if last_sentence and last_category:
            results.append((last_sentence.strip(), last_category))

        # If there are no results, classify the current sentence and append the sentence and its category to the results list
        if not results:
            max_category = max_label(classify_text(
                labels, current_sentence.strip()))
            if max_category:
                results.append((current_sentence.strip(), max_category))

        return results

    # If the review text exists and is longer than 25 characters, it is segmented into sentences and analyzed.
    if review_item['text'] and len(review_item['text']) > 25:
        sentences = segment_text(review_item["text"], language)
        return [format_results(sentence_analyse(sentence), review_item, entity, categories=labels) for sentence in sentences]

    return []


def get_data_from_api(url, bearer_token, params=None):
    """
    Fetches data from an API with a bearer token and optional parameters.

    Args:
      url: The API endpoint URL.
      bearer_token: The bearer token for authentication.
      params: A dictionary of query parameters.

    Returns:
      The response object from the API call.
    """
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    response = None

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful

    except requests.exceptions.RequestException as err:
        print("An error occurred:")
        print(err)
        print(traceback.format_exc())

    return response


def post_data_to_api(url, bearer_token, data):
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }

    response = None

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception if the request was unsuccessful

    except requests.exceptions.RequestException as err:
        print("An error occurred:")
        print(traceback.format_exc())

    return response


def post_classifications(datas):
    """
    This function uploads the classifications to the API.

    Args:
    datas (list): A list of dictionaries containing the classifications.

    Returns:
    dict: The JSON response from the API.
    """
    # Print the data to be uploaded for debugging purposes
    print("\n Datas: ", datas, '\n')
    print("Uploading classifications ...")

    # Define the API endpoint URL
    url = f"https://api-dev.nexties.fr/api/classification/upload"
    # Define the bearer token for authentication
    bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MTY4OTAxNjAsImV4cCI6MzI3MjA5MDE2MCwicm9sZXMiOlsiUk9MRV9FUkVQIiwiUk9MRV9DVVNUT01FUiIsIlJPTEVfUEFSVE5FUiIsIlJPTEVfVVNFUiJdLCJ1c2VybmFtZSI6ImxhdXJlbnppb3NhbWJhbnlAZ21haWwuY29tIn0.AfCjRneev40fepe1YuPdI22BoHQznaYkAGyee19dxiYhBWR8YAr15HbhL4ewNyyoglazQTVaW4HmI5AmUIKG7L8_PhzJkso0F4o6W5Tpf8T-xvhv_eB1STM39DEmFx3DPDDxABdbm7Xxc1BE5trSBQ_mIz1d-Rcebkej7Rg4SCGHL0Wv6GJlhFH3RVB87y49ETQDWCK4icU4UKlo-q6CW2HzAEct3cXk6vWhU93sw8y_iqFmlvCKU_cMdb1BTqsqohZYQ1Nt2k8xNRiNBcl4yazWrI-2qJS33e9IUkjib5jWfnsvMuA8BzntozZk2ieD-K5MfavT1nyuRij5BI018w"

    # Send a POST request to the API endpoint with the data and bearer token
    response = post_data_to_api(url, bearer_token, data={
                                "data_content": datas})

    # If the request was successful, print a success message and return the JSON response
    if response.status_code == 200:
        data = response.json()
        print("Uploaded successfully !")
        return data
    # If the request was unsuccessful, print an error message and return None
    else:
        print(f"Error: {response.status_code}")
        return None


def get_reviews(page=1, limit=10):
    """
    Fetches reviews from the API for a specific establishment.

    Args:
      page: The page number of the reviews to fetch.
      limit: The maximum number of reviews to fetch per page.

    Returns:
      The JSON response from the API call.
    """
    # Define the establishment tag
    tag = "652d515ba431b"  # 28-50
    # tag = "645de52f135e8" # Chalets du berger
    # tag = "66a21d3f105b8" # Hotel Lux Grand Gaube

    # Define the API endpoint URL
    url = f"https://api-dev.nexties.fr/api/establishment/{tag}/reviews_to_classify"

    # Define the bearer token for authentication
    bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MTY4OTAxNjAsImV4cCI6MzI3MjA5MDE2MCwicm9sZXMiOlsiUk9MRV9FUkVQIiwiUk9MRV9DVVNUT01FUiIsIlJPTEVfUEFSVE5FUiIsIlJPTEVfVVNFUiJdLCJ1c2VybmFtZSI6ImxhdXJlbnppb3NhbWJhbnlAZ21haWwuY29tIn0.AfCjRneev40fepe1YuPdI22BoHQznaYkAGyee19dxiYhBWR8YAr15HbhL4ewNyyoglazQTVaW4HmI5AmUIKG7L8_PhzJkso0F4o6W5Tpf8T-xvhv_eB1STM39DEmFx3DPDDxABdbm7Xxc1BE5trSBQ_mIz1d-Rcebkej7Rg4SCGHL0Wv6GJlhFH3RVB87y49ETQDWCK4icU4UKlo-q6CW2HzAEct3cXk6vWhU93sw8y_iqFmlvCKU_cMdb1BTqsqohZYQ1Nt2k8xNRiNBcl4yazWrI-2qJS33e9IUkjib5jWfnsvMuA8BzntozZk2ieD-K5MfavT1nyuRij5BI018w"

    # Define the query parameters
    params = {"all": "yes", "type": "reviews", "page": page, 'limit': limit}

    # Send a GET request to the API endpoint with the parameters and bearer token
    response = get_data_from_api(url, bearer_token, params)

    if response.status_code == 200:
        data = response.json()
        print(data)
        return data

    else:
        print(f"Error: {response.status_code}")
    # If the request was successful, print the JSON response and return it
    if response.status_code == 200:
        data = response.json()
        print(data)
        return data
    # If the request was unsuccessful, print an error message and return None
    else:
        print(f"Error: {response.status_code}")
        return None


def get_all_reviews():
    results = []

    # Define the labels for text classification
    labels = ["Fourniture", "Food", "Location",
              "Welcome", "Confort", "Service"]
    page = 1
    while True:
        print(f"\n====== Retrieving page {page} ======\n")
        data = get_reviews(page=page)

        if data:
            for review in data['reviews']:
                # Check if the review language is English
                if review['language'] and review['language'] == 'en':
                    print(f"\nText => {review['text']}:\n")
                    # Analyze the text and classify it into categories
                    result = analyse_text(
                        review, labels, entity='review', min_score=0.7, language='en')
                    print(f"\nResult => {result}\n")
                    results.extend(result)

            # If there are results, post them to the API
            if len(results):
                post_classifications(results)

            # Reset the results list for the next page
            results = []

            # Increment the page number for the next iteration
            page += 1
        else:
            break

# Add comments to explain the purpose and functionality of the code
# This function retrieves reviews from the API, analyzes the text of each review,
# classifies it into categories, and posts the results to the API.
# The function uses a while loop to retrieve all pages of reviews,
# and it checks the language of each review to ensure that it is English.
# The function also uses the analyse_text function to classify the text into categories,
# and it uses the post_classifications function to post the results to the API.


# get_all_reviews()


def get_score(classifier, text):
    """
    This function takes a classifier and a text as input, and returns the score of the text.
    It tries to replace any double quotes in the text with single quotes and pass it to the classifier.
    If an exception occurs, it prints the exception and returns False.
    Args:
    classifier: The classifier to be used for scoring the text.
    text: The text to be scored.

    Returns:
    The score of the text if successful, False otherwise.
    """
    try:
        # Replace double quotes with single quotes in the text
        # and pass it to the classifier to get the score
        return classifier(text.replace('\"', "\'"))
    except Exception as e:
        # If an exception occurs, print the exception and return False
        print(e)
        return False


def compute_sentiment(text):
    """
    This function computes the sentiment of a given text using a pre-trained model.
    It uses the 'nlptown/bert-base-multilingual-uncased-sentiment' model for sentiment analysis.
    The function returns a dictionary containing the confidence score and the sentiment label ('positive', 'negative', or 'neutral').
    If the sentiment analysis fails, the function returns False.
    """
    # Define the name of the pre-trained model
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"

    # Load the pre-trained model and tokenizer
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Create a sentiment analysis pipeline using the model and tokenizer
    classifier = pipeline('sentiment-analysis', model=model,
                          tokenizer=tokenizer, device=-1)

    # Get the sentiment score and label for the input text
    score_data = get_score(classifier, text)

    # If the sentiment analysis was successful
    if score_data:
        # Extract the confidence score and sentiment label from the score data
        confidence = score_data[0]['score']
        score_label = score_data[0]['label']

        # Convert the sentiment label to a star rating and sentiment category
        score_stars = int(score_label.split()[0])
        feeling = "negative" if score_stars < 3 else (
            "positive" if score_stars > 3 else "neutral")

        # Return a dictionary containing the confidence score and sentiment category
        return {'confidence': confidence, 'feeling': feeling}

    # If the sentiment analysis failed, return False
    return False


# This function is used to post sentiments to a specified URL.
def post_sentiments(datas):
    # Print the data that is being uploaded for debugging purposes.
    print("\n Datas: ", datas, '\n')

    # Print a message to indicate that the sentiments are being uploaded.
    print("Uploading sentiments ...")

    # Define the bearer token for authentication.
    bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MTY4OTAxNjAsImV4cCI6MzI3MjA5MDE2MCwicm9sZXMiOlsiUk9MRV9FUkVQIiwiUk9MRV9DVVNUT01FUiIsIlJPTEVfUEFSVE5FUiIsIlJPTEVfVVNFUiJdLCJ1c2VybmFtZSI6ImxhdXJlbnppb3NhbWJhbnlAZ21haWwuY29tIn0.AfCjRneev40fepe1YuPdI22BoHQznaYkAGyee19dxiYhBWR8YAr15HbhL4ewNyyoglazQTVaW4HmI5AmUIKG7L8_PhzJkso0F4o6W5Tpf8T-xvhv_eB1STM39DEmFx3DPDDxABdbm7Xxc1BE5trSBQ_mIz1d-Rcebkej7Rg4SCGHL0Wv6GJlhFH3RVB87y49ETQDWCK4icU4UKlo-q6CW2HzAEct3cXk6vWhU93sw8y_iqFmlvCKU_cMdb1BTqsqohZYQ1Nt2k8xNRiNBcl4yazWrI-2qJS33e9IUkjib5jWfnsvMuA8BzntozZk2ieD-K5MfavT1nyuRij5BI018w"

    # Send a POST request to the API with the data and bearer token.
    response = post_data_to_api(url, bearer_token, data={
                                'data_content': datas})

    # If the request was successful (status code 200), print the response data and a success message.
    if response.status_code == 200:
        data = response.json()
        print(data)
        print("Uploaded successfully !")
        return data

    # If the request was not successful, print the error status code.
    else:
        print(f"Error: {response.status_code}")
        return None

# Example usage:


def get_sections(page=1, limit=10):
    """
    This function retrieves data from the Nexties API based on the provided page and limit parameters.
    It uses a bearer token for authentication and a specific tag to filter the data.

    Parameters:
    page (int): The page number of the data to retrieve. Default is 1.
    limit (int): The number of data items to retrieve per page. Default is 10.

    Returns:
    data (dict): The JSON data retrieved from the API if the request is successful.
    None: If the request is not successful.
    """

    # The tag used to filter the data. Change this value to retrieve data for a different tag.
    tag = "652d515ba431b"

    # The URL of the Nexties API endpoint.
    url = "https://api-dev.nexties.fr/api/customer/classifications"

    # The bearer token used for authentication.
    bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MTY4OTAxNjAsImV4cCI6MzI3MjA5MDE2MCwicm9sZXMiOlsiUk9MRV9FUkVQIiwiUk9MRV9DVVNUT01FUiIsIlJPTEVfUEFSVE5FUiIsIlJPTEVfVVNFUiJdLCJ1c2VybmFtZSI6ImxhdXJlbnppb3NhbWJhbnlAZ21haWwuY29tIn0.AfCjRneev40fepe1YuPdI22BoHQznaYkAGyee19dxiYhBWR8YAr15HbhL4ewNyyoglazQTVaW4HmI5AmUIKG7L8_PhzJkso0F4o6W5Tpf8T-xvhv_eB1STM39DEmFx3DPDDxABdbm7Xxc1BE5trSBQ_mIz1d-Rcebkej7Rg4SCGHL0Wv6GJlhFH3RVB87y49ETQDWCK4icU4UKlo-q6CW2HzAEct3cXk6vWhU93sw8y_iqFmlvCKU_cMdb1BTqsqohZYQ1Nt2k8xNRiNBcl4yazWrI-2qJS33e9IUkjib5jWfnsvMuA8BzntozZk2ieD-K5MfavT1nyuRij5BI018w"

    # The parameters to include in the API request.
    params = {"page": page, 'limit': limit}

    # Send a GET request to the API endpoint with the bearer token and parameters.
    response = get_data_from_api(url, bearer_token, params)

    # If the request is successful, return the JSON data.
    if response.status_code == 200:
        data = response.json()
        return data

    # If the request is not successful, print the error status code and return None.
    else:
        print(f"Error: {response.status_code}")
        return None


# This function fetches all sections from a website
def get_all_sections():
    # Start from the first page
    page = 1
    # Continue fetching pages until there are no more pages left
    while True:
        # Print the current page number for tracking progress
        print(f"\n====== Fetching page {page} ======\n")
        # Fetch the data for the current page
        data = get_sections(page=page)

        # Print the data for debugging purposes
        print(data)
        # If there is no data or we've reached the last page, break the loop
        if not data or data['last_pages'] < page:
            break

        # Process the data for the current page
        results = process_page_data(data)
        # If there are results, post the sentiments
        if results:
            post_sentiments(results)

        # Move on to the next page
        page += 1


# This function processes the data from a page and computes the sentiment of each section.
def process_page_data(data):
    # Initialize an empty list to store the results.
    results = []

    # Loop through each item in the data.
    for line in data['items']:
        # Get the section of the current item.
        section = line['section']

        # If the section exists and contains more than one word, compute its sentiment.
        if section and len(section.split()) > 1:
            # Compute the sentiment of the section.
            score = compute_sentiment(section)

            # If the sentiment score exists, add the item's id, feeling, and confidence to the results.
            if score:
                results.append({
                    'id': line['id'],  # The id of the item.
                    # The sentiment of the section.
                    'feeling': score['feeling'],
                    # The confidence of the sentiment score.
                    'confidence_feeling': str(score['confidence'])
                })

    # Return the results.
    return results

# get_all_sections()