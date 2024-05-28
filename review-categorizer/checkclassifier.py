from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


def checkclassifier(categories, text):
    try:
        classifier = pipeline(task="zero-shot-classification",
                              device=-1, model="facebook/bart-large-mnli")

        prediction = classifier(
            text, list(map(lambda x: x['category'], categories)), multi_label=False)

        print(prediction)

    except Exception as e:
        print(e)
        pass


categs = []
texts = []

for t in texts:
    checkclassifier(categs, t)
