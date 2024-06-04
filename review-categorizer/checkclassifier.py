from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


def checkclassifier(categories, text):
    try:
        prediction = {'séquence': text, 'labels': [], 'scores': []}
        classifier = pipeline(task="zero-shot-classification",
                              device=-1, model="facebook/bart-large-mnli")

        # categs = list(map(lambda x: x['category'], categories))
        categs = categories

        for categ in categs:
            result = classifier(text, categ, multi_label=False)

            # print(result)
            prediction['labels'].append(categ)
            prediction['scores'].append(result['scores'][0])

        # prediction = classifier(
           # text, list(map(lambda x: x['category'], categories)), multi_label=False)
            # text, categories, multi_label=True)

        print('\n', prediction)

    except Exception as e:
        print(e)
        pass


categs = ['Furniture', 'Home', 'Housekeeping', 'Location', 'Food']
texts = [
    'Very pleasant and welcoming staff. Complete apartment equipment. Accommodation a little aging however with some small improvement work to be planned but well equipped... We would nevertheless have liked to have a terrace on the sun side and a clear view but that was not possible...; too bad!',
    'We enjoyed our stay despite a few details which spoiled the weekend a little. The residence was found to be aging. It could do with a refresh. After a day of hiking we would have appreciated the swimming pool\xa0… Read more',
    'Family stay during the Easter holidays in an apartment. The accommodation is spacious, well equipped, well soundproofed. The beds are comfortable, the individual heating efficient for a cocooning atmosphere despite the cold outside. Precision,\xa0…',
    'The studios are small but nice. The location is ideal near the slopes. The big flaw is that the apartments are overheated like in a sauna and the water in the swimming pool is very cold! Can\'t we balance all of this?',
    'Arrival was a little complicated (due to a late arrival we had the wrong room number in the envelope) but after a phone call, the problem was quickly rectified! In terms of breakfast, we were a little disappointed by\xa0…',
    'Family stay during the Easter holidays in an apartment. The accommodation is spacious, well equipped, well soundproofed. The beds are comfortable, the individual heating efficient for a cocooning atmosphere despite the cold outside. Accuracy,\xa0… Learn more',
    'Small place perched in the mountain, but worth the detour. We spent a pleasant weekend surrounded by nature, a nice little village and a top residence.\xa0…',
    'Very disappointed not to have a balcony although it is clearly highlighted in the photos on the site. Furthermore, I do not find it normal that customers are obliged to remove sheets\xa0… Find out more',
    'The studios are small but nice. The location is ideal near the slopes. The big flaw is that the apartments are overheated like in a sauna and the water in the swimming pool is very cold! Can\'t we balance all of this?'
]

for t in texts:
    checkclassifier(categs, t)
