from api import ERApi
import json


class EReputationBase:

    def __init__(self, rid:int=-1) -> None:
        self.id = rid
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
            req = ERApi(method="post", entity='social_pages')
            req.set_body(data)
            res = req.execute()
        
        return res

    def extract_id(self, foreign_key: str) -> str:
        return foreign_key.split('/')[2]

    def get_elements(self, attribute: str) -> list:
        if self.id != -1 and len(getattr(self, attribute, [])):

            return getattr(self, attribute)
        return []


class SocialPage(EReputationBase):
    def __init__(self, rid:int=-1) -> None:
        super().__init__(rid)
        self.source = ""
        self.followers = 0
        self.likes = 0
        self.posts = 0
        self.entity = "social_pages"


class SocialPost(EReputationBase):
    def __init__(self, rid:int=-1):
        super().__init__(rid)
        self.title = 0
        self.likes = 0
        self.comments = 0
        self.share = 0
        self.socialPage = ""
        self.publishedAt = ""
        self.entity = "social_posts"


__class_name__ = {
    'social_posts': SocialPost,
    'social_pages': SocialPage
}


def create(entity:str="", data:dict={}):
    instance = __class_name__[entity]()

    for key in data.keys():
        setattr(instance, key, data[key])
    
    return instance
