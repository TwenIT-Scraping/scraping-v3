from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


def checkclassifier(categories, text):
    try:
        prediction = {'séquence': text, 'labels': [], 'scores': [] }  
        classifier = pipeline(task="zero-shot-classification",
                              device=-1, model="facebook/bart-large-mnli")
        
        # categs = list(map(lambda x: x['category'], categories))
        categs = categories
        
        for categ in categs:
            result = classifier(text, categ, multi_label=False)

            print(result)
            prediction['labels'].append(categ)
            prediction['scores'].append(result['scores'][0])

        # prediction = classifier(
           # text, list(map(lambda x: x['category'], categories)), multi_label=False)
            # text, categories, multi_label=True)

        print('\n', prediction)

    except Exception as e:
        print(e)
        pass


categs = ['Mobilier', 'Ménage', 'propreté']
texts = ['« Ménage parfait »: Les équipements, la propreté, le calme et la situation géographique. Le style des bâtiments. | Un petit entretien du mobilier des boiseries et autres']

for t in texts:
    checkclassifier(categs, t)
