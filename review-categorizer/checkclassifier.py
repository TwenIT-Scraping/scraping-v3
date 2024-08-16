from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from progress.bar import FillingCirclesBar
import spacy


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

    excepted_token = ["AND", "ET"]

    for token in doc:
        # print(token.text, " => ", token.pos_)

        if token.pos_ in ["PUNCT", "CCONJ", "ADV"] and token.text.upper() not in excepted_token:
            # print(f"Separator found: {token.text}")

            if sentence != "":
                if token.text == "," and word_count >= 3:
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
            line = ""

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
        filtered_labels = [label for label,
                           score in labels_with_score if score >= score_min]
        return filtered_labels

    categories = []
    # classifier = pipeline('zero-shot-classification',
    #                       model='facebook/bart-large-mnli')
    classifier = pipeline('zero-shot-classification',
                          device=-1, model='cross-encoder/nli-deberta-v3-base')

    aspect_terms = []

    # omit the segmentation if full_text is True
    if full_text:
        aspect_terms = segment_by_length(text)

    # segment the text
    else:
        aspect_terms = segment_text(text)

    # get the categories for each aspect term
    sentence_categories = []

    for term in aspect_terms:
        result = classifier(term, candidate_labels, multi_label=True)

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

    categories.append(sentence_categories)

    return categories

#######################################################
# Compute global categories then categorize each term using them #
# Expected results : [(term, [catégorie1, catégorie2, ...]), ...] #
#######################################################


def get_categories(text, score_min, labels):
    global_aspect_categories = detect_aspect_category(
        text, labels, score_min, True)
    global_categories = []

    for aspect_category in global_aspect_categories:
        for category in aspect_category[1]:
            if category not in global_categories:
                global_categories.append(category)

    aspect_categories = detect_aspect_category(
        text, global_categories, score_min, False)

    return aspect_categories
