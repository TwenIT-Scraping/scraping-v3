from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
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

    return sentence_categories

#######################################################
# Compute global categories then categorize each term using them #
# Expected results : [(term, [catégorie1, catégorie2, ...]), ...] #
#######################################################


def get_categories(text, labels):
    global_aspect_categories = detect_aspect_category(
        text, labels, 0.6, True)
    global_categories = []

    for aspect_category in global_aspect_categories:
        for category in aspect_category[1]:
            if category[0] not in global_categories:
                global_categories.append(category[0])

    if len(global_categories) == 0:
        return []

    aspect_categories = detect_aspect_category(
        text, global_categories, 0.8, False)

    return aspect_categories


def concat_sequences_by_label(categories, score_min=0.8):
    """
    Concatenates sequences for each label with a score greater than 0.8.

    Args:
      categories: A list of tuples, where each tuple contains a sequence and a list of (label, score) pairs.

    Returns:
      A dictionary mapping labels to concatenated sequences.
    """

    label_sequences = {}

    for sequence, label_scores in categories:
        for label, score in label_scores:
            if score >= score_min:
                if label not in label_sequences:
                    label_sequences[label] = []
                    label_sequences[label].append((sequence, score))
                else:
                    label_sequences[label].append((sequence, score))

    for label, sequences in label_sequences.items():
        score_avg = 0

        for sequence, score in sequences:
            score_avg += score
        score_avg /= len(sequences)

        label_sequences[label] = (" | ".join([seq[0]
                                  for seq in sequences]), score_avg)

    return label_sequences


def transform_to_json(concatenated_sequences, line_id, column_name):
    """
    Transforms the result of concat_sequences_by_label to a JSON object.

    Args:
      concatenated_sequences: A dictionary mapping labels to concatenated sequences and their average scores.

    Returns:
      A list of dictionaries, where each dictionary represents a category with its sequence and score.
    """

    json_result = []

    for category, (sequence, score) in concatenated_sequences.items():
        json_result.append({
            "category": category,
            "section": sequence,
            "confidence": score,
            f"${column_name}": line_id
        })

    return json_result

#######################################################
# Main categorization #
# Expected results : [{"category": "...", "sequence": ..., "score": ...}, ...] #
#######################################################


def ia_categorize(line, column, labels):
    categories = get_categories(line['text'], labels)
    concatenated_sequences = concat_sequences_by_label(categories, 0.8)
    return transform_to_json(concatenated_sequences, line[id], column)
