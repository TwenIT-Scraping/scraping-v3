from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import spacy

# Function to classify text using a zero-shot classification model
# This function takes a list of categories and a text as input
# It returns the result of the classification


def classify_text(categories, text):
    # Initialize the zero-shot classification pipeline with the specified model
    # The device is set to -1 to use the CPU
    classifier = pipeline('zero-shot-classification',
                          device=-1, model='cross-encoder/nli-deberta-v3-base')

    # Classify the text using the provided categories
    # The multi_labels parameter is set to True to allow multiple categories for a single text
    result = classifier(text, categories, multi_labels=True)

    # Return the result of the classification
    return result

###################################################
# Ségmentation de texte utilisant la librairie spacy qui consiste à découper
# le texte lorsqu'on croire les adverbes, poctuations et conjonctions #
###################################################


def segment_text(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    sentence = ""
    word_count = 0

    result = []

    excepted_token = ["AND", "ET", "THAT"]

    for token in doc:

        if (token.pos_ in ["PUNCT", "CCONJ", "ADV"] and token.text.upper() not in excepted_token) or token.text == "|":

            if sentence != "":
                if (token.text == "," or token.text == "|") and word_count >= 3:
                    result.append(sentence)
                    sentence = ""
                    word_count = 0
                elif token.text == "," and word_count < 3:
                    sentence = "".join([sentence, token.text])
                    word_count += 1
                else:
                    result.append(sentence)
                    sentence = ""
                    word_count = 0

        else:
            sentence = " ".join([sentence, token.text])
            word_count += 1

    if sentence != "":
        result.append(sentence.strip())

    return result

################################################################
# Ségmenter le texte en segments de longueur maximale spécifiée. #
# Résultat attendu : [segment1, segment2, ...]                   #
################################################################


def segment_by_length(text, max_length=512):

    segments = []
    line = ""

    terms = segment_text(text)

    for term in terms:
        if len(line) <= max_length:
            line += " " + term
        else:
            segments.append(line.strip())
            line = term

    if line != "":
        segments.append(line.strip())

    return segments

###################################################
# Segment the text and categorize each part #
# Expected result: [(term, [category1, category2, ...]), ...] #
###################################################


def detect_aspect_category(text, candidate_labels, score_min=.8, full_text=False):

    ### Get label with score > score_min ###

    def get_labels(data, score_min):
        labels_with_score = list(zip(data['labels'], data['scores']))
        filtered_labels = [(label, score) for label,
                           score in labels_with_score if score >= score_min]
        return filtered_labels

    # classifier = pipeline('zero-shot-classification',
    #                       model='facebook/bart-large-mnli')
    classifier = pipeline('zero-shot-classification',
                          device=-1, model='cross-encoder/nli-deberta-v3-base')

    aspect_terms = []
    # print("\t\t- segmentation step")

    # omit the segmentation if full_text is True
    if full_text:
        aspect_terms = segment_by_length(text)

    # segment the text
    else:
        aspect_terms = segment_text(text)

    # print("\t\t Results: ", aspect_terms)

    # get the categories for each aspect term
    sentence_categories = []

    # print("\t\t- Classification step with the categories: ", candidate_labels)

    for term in aspect_terms:
        result = classifier(term, candidate_labels, multi_label=True)
        print(result)

        ####### result format ########
        # {
        #         'labels': ['travel', 'cooking', 'dancing'],
        #         'scores': [0.444, 0.0111, 0.963],
        #         'sequence': line['text']
        #     }
        ################################

        # Get label with score > score_min

        top_categories = get_labels(result, score_min)
        sentence_categories.append((term, top_categories))

    # print("\t\t Results: ", sentence_categories)

    return sentence_categories

#######################################################
# Compute global categories then categorize each term using them #
# Expected results : [(term, [catégorie1, catégorie2, ...]), ...] #
#######################################################


def get_categories(text, labels):
    # print("\n\t1- Compute global categories")
    # print("\t\ta- Detect aspect categories")
    global_aspect_categories = detect_aspect_category(
        text, labels, 0.9, True)
    # print("\t\t => ", global_aspect_categories)
    global_categories = []

    # print("\t\tb- Compute global categories")

    for aspect_category in global_aspect_categories:
        for category in aspect_category[1]:
            if category[0] not in global_categories:
                global_categories.append(category[0])

    # print("\t\t => ", global_aspect_categories)

    if len(global_categories) == 0:
        return []

    # print("\n\t2- Compute sections categories")
    aspect_categories = detect_aspect_category(
        text, global_categories, 0.9, False)

    # print("\t\t => ", aspect_categories)

    print("\t\t => ", aspect_categories)

    return aspect_categories


def transform_to_json(sections, line_id, column_name, labels, score_min=0.8):
    """
    Transforms the sections to a JSON object.

    Args:
      sections: A list tuple with this form [(text,[(category, score), (category2, score2), ...], ...)] .

    Returns:
      A list of dictionaries, where each dictionary represents a category with its sequence and score.
    """

    json_result = []

    for text, categories in sections:
        if len(text.split()) >= 3:
            for label, score in categories:
                if score >= score_min:
                    line = {
                        "category": label,
                        "section": text,
                        "confidence": score,
                        f"{column_name}": str(line_id),
                        "checked": labels
                    }

                    # Complete missing keys with socialPost, socialComment and review
                    if 'review' not in line.keys():
                        line["review"] = ""

                    if 'socialPost' not in line.keys():
                        line["socialPost"] = ""

                    if 'socialComment' not in line.keys():
                        line["socialComment"] = ""

                    json_result.append(line)

    return json_result

#######################################################
# Main categorization #
# Expected results : [{"category": "...", "sequence": ..., "score": ...}, ...] #
#######################################################


def ia_categorize(line, column, labels):
    # print("\n ==== Get categories ====")
    categories = get_categories(line['text'], labels)
    # print("==== Results ====")
    print(categories)
    # print("===========================\n")
    print("\n==== transform to json ====")
    result = transform_to_json(categories, line['id'], column, labels, 0.9)
    # print("\n==== results ====")
    # print(result)
    print("================================\n")
    return result
