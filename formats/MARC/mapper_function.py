import json

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def split_to_each_field(n, input):
    lines = [input[i:i + n] for i in range(0, len(input), n)]
    return lines

def MapUNIMARC(file, model):
    list_of_items = []
    field_end = "\x1e"
    subfield = "\x1f"
    item_end = "\x1d"
    with open("models/"+model.name+"/mappers/unimarc.json") as unimarc_mapper:
        mapper_dict = json.load(unimarc_mapper)
    usable_mapper = []
    for x, y in mapper_dict["fields_map"].items():
        temp_mapper = {}
        map_field = x[:3]
        map_subfield = x[3:].replace("$","")
        for each in model.fields:
            if each.name == y:
                model_field = each
        temp_mapper = {"unimarc_field": map_field, "unimarc_subfield": map_subfield, "model_field": model_field}
        usable_mapper.append(temp_mapper)
    print(usable_mapper)
    one_type = mapper_dict["one_type"]
    with open(file, newline="", encoding="utf8") as bibfile:
        bibfile = bibfile.read()
        items = bibfile.split(item_end)
        del items[-1]
        for item in items:
            temp_item = {}
            for f in model.fields:
                if f.name != "id":
                    if f.is_many:
                        temp_item[f.name] = []
                    else:
                        temp_item[f.name] = ""
            base_address = int(item[12:17])
            bibliographic_level = item[7]
            full_index = item[24:base_address-1]
            fields_index = split_to_each_field(12, full_index)
            item_itself = item[base_address:]

            for field_info in fields_index:
                tag = field_info[:3]
                field_length = int(field_info[3:7])
                starting_char_pos = int(field_info[7:12])
                if not starting_char_pos:
                    starting_char_pos = 0
                field_itself = item_itself[starting_char_pos:starting_char_pos+field_length]

                for z in usable_mapper:
                    if z["unimarc_field"] == tag:
                        split_subfields = field_itself.split(subfield)
                        for splitted in split_subfields:
                            if splitted.startswith(z["unimarc_subfield"]):
                                print(splitted)
                                to_insert = splitted[1:].replace(field_end, "")
                                to_insert = to_insert.replace(item_end, "")
                                if z["model_field"].is_many:
                                    temp_item[z["model_field"].name].append(to_insert)
                                else:
                                    temp_item[z["model_field"].name] = to_insert

            #MAP TYPE OF PUBLICATION(BIBL. LEVEL)
            if one_type:
                model_type = mapper_dict["one_type"]
            else:
                model_type = mapper_dict["type_map"][bibliographic_level]
            temp_item["type"] = model_type
            list_of_items.append(temp_item)

    return list_of_items