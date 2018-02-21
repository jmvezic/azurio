import json

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def MapBIBTEX(file, model):
    list_of_items = []
    origin_items = []
    with open("models/"+model.name+"/mappers/bibtex.json") as bibtex_mapper:
        mapper_dict = json.load(bibtex_mapper)
    one_type = mapper_dict["one_type"]
    with open(file, newline="") as bibfile:
        bibfile = bibfile.readlines()
        for line in bibfile:
            if line.startswith("@"):
                origin_items.append(bibfile.index(line))
        i = 0
        for item in origin_items:
            temp_item = {}
            type_to_map = bibfile[item].split("{")[0]
            if one_type:
                model_type = mapper_dict["one_type"]
            else:
                model_type = mapper_dict["type_map"][type_to_map]
            temp_item["type"] = model_type
            fields_spread = []
            startno = item+1
            if item is not origin_items[-1]:
                endno = origin_items[i+1]-1
            else:
                endno = bibfile.index(bibfile[-1])
            while startno <= endno:
                fields_spread.append(startno)
                startno+=1
            print(fields_spread)
            for field_line in fields_spread:
                field_name = bibfile[field_line].split("=")[0]
                field_name = "".join(field_name.split())
                for bib_field, model_field in mapper_dict["fields_map"].items():
                    if bib_field == field_name:
                        for org_field in model.fields:
                            if org_field.name == model_field:
                                if org_field.is_many:
                                    temp_item[model_field] = [find_between(bibfile[field_line].split("=")[1], "{", "}")]
                                else:
                                    temp_item[model_field] = find_between(bibfile[field_line].split("=")[1], "{", "}")

            for mod_f in mapper_dict["fields_map"].values():
                if mod_f not in temp_item.keys():
                    for org_field in model.fields:
                        if org_field.name == mod_f:
                            if org_field.is_many:
                                temp_item[mod_f] = []
                            else:
                                temp_item[mod_f] = ""

            list_of_items.append(temp_item)
            i+=1
    return list_of_items