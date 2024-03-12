from api import ERApi
import json


class EReputationBase:

    def __init__(self, rid: int = -1, name: str = "") -> None:
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
            print(attribute, ': ', value)

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
    def __init__(self, rid: int = -1, name: str = "") -> None:
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
    def __init__(self, rid: int = -1, name: str = "") -> None:
        super().__init__(rid, name)
        self.address1 = ""
        self.address2 = ""
        self.zipcode = ""
        self.city = ""
        self.country = ""
        self.region = ""
        self.gps = ""
        self.competitor_tag = ""
        self.competitors = []
        self.customer = ""
        self.reviews = []
        self.websites = {}
        self.station_key = ""
        self.station_name = ""
        self.tag = ""
        self.entity = "establishments"

    def set_tag(self, tag):
        self.tag = tag

    def refresh(self) -> None:
        # super().refresh()
        self.website_urls()

    def website_urls(self) -> list:
        instance = ERApi(entity=f"establishment/{self.tag}/website")
        data = instance.execute()

        urls = {}
        url_fields = ['google', 'tripadvisor', 'opentable', 'trustpilot',
                      'expedia', 'camping', 'booking', 'hotels_com', 'maeva']

        for field in url_fields:
            if len(data) and data[0][field]:
                urls[field] = data[0][field]

        self.websites = urls


class Review(EReputationBase):
    def __init__(self, rid: int = -1, name: str = "") -> None:
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
    def save_multi(data_content, env):
        req = ERApi(method="postmulti", entity=f"reviews/multi", env=env)
        req.set_body({'data_content': data_content})
        res = req.execute()
        print(res.status_code)
        # print(res.text)


class Settings:
    def __init__(self, category=None, eid=None, source=None, ename=None, env="PROD"):
        self.eid = eid
        self.category = category
        self.ename = ename
        self.source = source
        self.items = []
        self.env = env

    def prepare(self):

        try:
            page = 0
            req = ERApi(method="get", entity="setting/list", env=self.env)

            self.eid and req.add_params({'eid': self.eid})
            self.category and req.add_params({'categ': self.category})
            self.ename and req.add_params({'ename': self.ename})
            self.source and req.add_params({'src': self.source})

            while True:
                page += 1
                req.add_params({'page': page})
                res = req.execute()

                if len(res) > 0:
                    self.items = self.items + res
                else:
                    break

        except Exception as e:
            print(e)
            raise Exception(
                "Des erreurs sont rencontrées durant l'initialisation !!!")

    @staticmethod
    def disable_setting(setting_id, env):
        print(f"// ***  Disable a setting: {setting_id} ... *** //")
        req = ERApi(method="patch", entity="settings",
                    id=setting_id, body={'enable': False}, env=env)
        res = req.execute()
        print(f"// **************** {res} ************** //")

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

# setts = Settings()
# setts.prepare()
