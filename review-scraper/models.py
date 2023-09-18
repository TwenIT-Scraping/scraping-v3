from api import ERApi
import json


class EReputationBase:

    def __init__(self, rid:int=-1, name:str="") -> None:
        self.id = rid
        self.name = name
        self.entity = "establishments"

    def refresh(self) -> None:
        req = ERApi(method="getone", entity=self.entity, id=self.id)
        res = req.execute()
        
        for key, value in res.items():
            setattr(self, key, value)

    def print(self) -> None:
        for attribute, value in self.__dict__.items():
            print(attribute,': ', value)

    def save(self) -> bool:
        data = self.__dict__
        if self.id != -1:
            req = ERApi(method="put", entity=self.entity, id=self.id)
            data.pop('id')
            data.pop('entity')
            req.set_body(data)
            res = req.execute()

        else:
            data.pop('id')
            entity = data.pop('entity')
            req = ERApi(method="post", entity=self.entity)
            req.set_body(data)
            res = req.execute()
        
        return res

    def extract_id(self, foreign_key: str) -> str:
        return foreign_key.split('/')[2]

    def get_elements(self, attribute: str) -> list:
        if self.id != -1 and len(getattr(self, attribute, [])):

            return getattr(self, attribute)
        return []


class Website(EReputationBase):
    def __init__(self, rid:int=-1, name:str="") -> None:
        super().__init__(rid, name)
        self.url = None
        self.accommodations = []
        self.regions = []
        self.google = None
        self.tripadvisor = None
        self.opentable = None
        self.trustpilot = None
        self.establishment = None,
        self.expedia = None
        self.camping = None
        self.booking = None
        self.maeva = None
        self.entity = "websites"


class Establishment(EReputationBase):
    def __init__(self, rid:int=-1, name:str="") -> None:
        super().__init__(rid, name)
        self.address1 = ""
        self.address2 = ""
        self.zipcode = ""
        self.city = ""
        self.country = ""
        self.region = ""
        self.gps = ""
        self.competitor_tag = ""
        self.competitors  = []
        self.customer = ""
        self.reviews = []
        self.websites = {}
        self.station_key = ""
        self.station_name = ""
        self.entity = "establishments"

    def refresh(self) -> None:
        super().refresh()
        self.website_urls()

    def website_urls(self) -> list:
        websites = self.get_elements("websites")
        urls = {}
        url_fields = ['google', 'tripadvisor', 'opentable', 'trustpilot', 'expedia', 'camping', 'booking']

        for website in websites:
            for field in url_fields:
                if website[field]:
                    urls[field] = website[field]
        
        self.websites = urls


class Review(EReputationBase):
    def __init__(self, rid:int=-1, name:str="") -> None:
        super().__init__(rid, name)
        self.entity = 'reviews'

    def __init__(self, review: dict) -> None:
        super().__init__(-1, "")
        self.entity = 'reviews'
        self.refresh(review)

    def refresh(self, review) -> None:
        for key in review.keys():
            setattr(self, key, review[key])

    @staticmethod
    def save_multi(data_content):
        req = ERApi(method="postmulti", entity=f"reviews/multi")
        req.set_body({'data_content': data_content})
        res = req.execute()
        # print(res.text)

# etab = Establishment(rid=2)
# etab.refresh()
# print(etab.websites)


# e1 = Website(rid=1)
# e1.refresh()
# # e1.region = 'Madagascar'
# e1.print()
# # e1.save()
# # ws = e1.get_elements("websites")
# # print(ws)
