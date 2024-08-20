



class Maeva_Field_Validator(object):

    def __init__(self, data:dict) -> None:
        self.data = data
        self.invalid_fields = []

    def price_is_valid(self, price_value:float) -> bool:
        if price_value == 0.00 or price_value == '':
            self.invalid_fields.append('price_value')
            return False
        try:
            x = float(price_value)
            if float(x) > 0:
                return True
            else:
                self.invalid_fields.append('price_value')
                return False
        except AttributeError:
            print(f"\t cannot convert {price_value} to float")
            return False
        
    def locality_is_valid(self, locality_value:str) -> bool:
        if locality_value != '':
            return True
        self.invalid_fields.append('locality')
        return False
    
    def typology_is_valid(self, typology_value:str) -> bool:
        if typology_value != '' and 'pers' in typology_value.lower():
            return True
        self.invalid_fields.append('typology')
        return False
    
    def name_is_valid(self, name_value:str) -> bool:
        if name_value != '':
            return True
        self.invalid_fields.append('nom')
        return False
    
    def noffre_is_valid(self, noffre_value:str) -> bool:
        try:
            int(noffre_value)
            return True
        except:
            self.invalid_fields.append('n_offre')
            return False
        

    def is_valid(self) -> object:
        print('validating ...')
        if self.price_is_valid(self.data['prix_actuel']) and \
            self.price_is_valid(self.data['prix_init']) and \
            self.locality_is_valid(self.data['localite']) and \
            self.name_is_valid(self.data['nom']) and \
            self.noffre_is_valid(self.data['n_offre']) and \
            self.typology_is_valid(self.data['typologie']):
            return self.invalid_fields , True
        else:
            return self.invalid_fields , False 
    