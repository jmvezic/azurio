class ModelField:
    def __init__(self, name, label, is_many=False, transform=str, validate=bool):
        self.name = name
        self.label = label
        self._transform = transform
        self._validate = validate
        self.is_many = is_many

class ModelType:
    def __init__(self, name, label, mandatory_atts, optional_atts):
        self.name = name
        self.label = label
        self.mandatory_atts = mandatory_atts
        self.optional_atts = optional_atts

class DataModel:
     def __init__(self, name, data_types):
         self.name = name
         self.data_types = data_types
         self.fields = []
         self.types = {}
         for datatype in self.data_types:
             self.types.update({datatype.label: datatype})
             for mandatory in datatype.mandatory_atts:
                if mandatory not in self.fields:
                    self.fields.append(mandatory)
             for optional in datatype.optional_atts:
                 if optional not in self.fields:
                    self.fields.append(optional)
         #self.fields.append(id)
         #self.fields.append(type)