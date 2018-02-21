import json
from class_model import *
import os

models_files_list = []
models = {}


for root, dirs, files in os.walk("models/"):
    for dir in dirs:
        models_files_list.append(dir)
    break

# for file in os.listdir("models"):
#     if file.endswith(".json"):
#         models_files_list.append(file)

#print(models_files_list)

for model_file in models_files_list:
    with open('models/' + model_file + "/model.json") as json_data:
        d = json.load(json_data)
    #print(d["fields"])
    model_name = model_file
    fields_list = []
    types_list = []

    for x,y in d["fields"].items():
        if y["ismany"] is True:
            ismany = True
        elif y["ismany"] is False:
            ismany = False
        if y["transform"] == "str":
            trans = str
        elif y["transform"] == "int":
            trans = int

        new_field = ModelField(y["name"], y["label"], ismany, trans)
        fields_list.append(new_field)

    for x,y in d["types"].items():
        mandatories = y["mandatory"]
        optionals = y["optional"]
        mand_list = mandatories.split(",")
        mand_list = list(filter(None, mand_list))
        opt_list = optionals.split(",")
        opt_list = list(filter(None, opt_list))

        mand_object_list = []
        opt_object_list = []
        for n in mand_list:
            for j in fields_list:
                if n == j.name:
                    mand_object_list.append(j)

        for n in opt_list:
            for j in fields_list:
                if n == j.name:
                    opt_object_list.append(j)

        new_type = ModelType(y["name"],y["label"],mand_object_list, opt_object_list)
        types_list.append(new_type)

    new_model = DataModel(model_name, types_list)
    models[new_model.name] = {"name": new_model.name, "object": new_model}

# with open('models/Moj model.json') as json_data:
#     d = json.load(json_data)
#     print(d)

print(models)