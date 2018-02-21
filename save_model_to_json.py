import json
import os

def SaveToJson(model_object):
    name = model_object.name
    model_dict = {"types":{},"fields":{}}
    fields_object_list = []
    for type in model_object.data_types:
        model_dict["types"][type.name] = {"name": type.name, "label": type.label}
        mandat = ""
        optio = ""
        for x in type.mandatory_atts:
            if x not in fields_object_list:
                fields_object_list.append(x)
            mandat = mandat + x.name + ","
        for x in type.optional_atts:
            if x not in fields_object_list:
                fields_object_list.append(x)
            optio = optio + x.name + ","
        model_dict["types"][type.name].update({"mandatory": mandat, "optional": optio})
    for x in fields_object_list:
        model_dict["fields"][x.name] = {"name": x.name, "label": x.label, "ismany": x.is_many}
        if x._transform is str:
            model_dict["fields"][x.name].update({"transform": "str"})
        elif x._transform is int:
            model_dict["fields"][x.name].update({"transform": "int"})

    if not os.path.exists("models/" + name):
        os.makedirs("models/" + name)
        os.makedirs("models/{}/{}".format(name, "cit_mappers"))
        os.makedirs("models/{}/{}".format(name, "mappers"))
        os.makedirs("models/{}/{}".format(name, "styles"))

    with open('models/' + name + '/model.json', 'w') as fp:
        json.dump(model_dict, fp)