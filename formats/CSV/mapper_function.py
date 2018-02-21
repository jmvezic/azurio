import csv
import json

def MapCSV(file, model, mapper):
    positions = {}
    not_present = []
    list_of_items = []
    with open("models/"+model.name+"/mappers/csv.json") as csv_mappers:
        mappers_dict = json.load(csv_mappers)
    if mappers_dict[mapper]["delimiter"]:
        delimt = mappers_dict[mapper]["delimiter"]
    else:
        delimt = "\t"
    one_type = mappers_dict[mapper]["one_type"]
    with open(file, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=delimt)
        headers = []
        for row in reader:
            headers = row
            break

        for x, y in mappers_dict[mapper]["fields_map"].items():
            if x in headers:
                positions[y] = row.index(x)
            else:
                not_present.append(y)

        print(positions)

        i = 0
        for row in reader:
            if i == 0:
                pass
            else:
                item_for_list = {}
                for a, b in positions.items():
                    if a == "type":
                        item_for_list[a] = mappers_dict[mapper]["type_map"][row[b]]
                    else:
                        for field in model.fields:
                            if field.name == a:
                                if field.is_many:
                                    item_for_list[a] = [row[b]]
                                else:
                                    item_for_list[a] = row[b]
                for x in not_present:
                    for field in model.fields:
                        if field.name == a:
                            if field.is_many:
                                item_for_list[x] = [""]
                            else:
                                item_for_list[x] = ""
                list_of_items.append(item_for_list)
            i+=1
    return list_of_items