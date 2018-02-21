def SpecificCases(case_o, value_o):
    if case_o == "CaseSentence":
        new = value_o.capitalize()
    elif case_o == "CaseTitle":
        new = value_o.title()
    elif case_o == "CaseUpper":
        new = value_o.upper()
    elif case_o == "CaseLower":
        new = value_o.lower()
    return new

def ChangeCase(collection, field, case, allitems):
    reporter = []
    for x, y in collection._data.items():
        one_item = ""
        old = y[field.name]
        if allitems:
            old = y[field.name]
            if type(old) is list:
                temp_list = []
                for value in old:
                    new = SpecificCases(case, value)
                    temp_list.append(new)
                y[field.name] = temp_list
            else:
                new = SpecificCases(case, old)
                y[field.name] = new
        else:
            if y["id"] in collection._selected_items:
                old = y[field.name]
                if type(old) is list:
                    temp_list = []
                    for value in old:
                        new = SpecificCases(case, value)
                        temp_list.append(new)
                    y[field.name] = temp_list
                else:
                    new = SpecificCases(case, old)
                    y[field.name] = new
        if old != y[field.name]:
            one_item = "<b>({})</b> {} --> {} (ID#{})".format(field.label, old, y[field.name], str(y["id"]))
            reporter.append(one_item)
    return reporter

def Replace(collection, field, replacefrom, replaceto, allitems):
    reporter = []
    for x, y in collection._data.items():
        one_item = ""
        old = y[field.name]
        if allitems:
            old = y[field.name]
            if type(old) is list:
                temp_list = []
                for value in old:
                    new = value.replace(replacefrom, replaceto)
                    temp_list.append(new)
                y[field.name] = temp_list
            else:
                new = old.replace(replacefrom, replaceto)
                y[field.name] = new
        else:
            if y["id"] in collection._selected_items:
                old = y[field.name]
                if type(old) is list:
                    temp_list = []
                    for value in old:
                        new = value.replace(replacefrom, replaceto)
                        temp_list.append(new)
                    y[field.name] = temp_list
                else:
                    new = old.replace(replacefrom, replaceto)
                    y[field.name] = new
        if old != y[field.name]:
            one_item = "<b>({})</b> {} --> {} (ID#{})".format(field.label, old, y[field.name], str(y["id"]))
            reporter.append(one_item)
    return reporter

def Split(collection, field, splitby, allitems):
    reporter = []
    if field.is_many:
        for x, y in collection._data.items():
            one_item = ""
            old = y[field.name]
            if allitems:
                old = y[field.name]
                temp_list = []
                for value in old:
                    new = value.split(splitby)
                    for each in new:
                        temp_list.append(each)
                y[field.name] = temp_list
            else:
                if y["id"] in collection._selected_items:
                    old = y[field.name]
                    temp_list = []
                    for value in old:
                        new = value.split(splitby)
                        for each in new:
                            temp_list.append(each)
                    y[field.name] = temp_list
            if old != y[field.name]:
                one_item = "<b>({})</b> {} --> {} (ID#{})".format(field.label, old, y[field.name], str(y["id"]))
                reporter.append(one_item)
    return reporter

def Inverse(collection, field, inverseby, allitems):
    reporter = []
    for x, y in collection._data.items():
        one_item = ""
        old = y[field.name]
        if allitems:
            old = y[field.name]
            if type(old) is list:
                temp_list = []
                for value in old:
                    new = value.split(inverseby)
                    new = new[1] + " " + new[0]
                    temp_list.append(new)
                y[field.name] = temp_list
            else:
                new = old.split(inverseby)
                new = new[1]+ " " + new[0]
                y[field.name] = new
        else:
            if y["id"] in collection._selected_items:
                old = y[field.name]
                if type(old) is list:
                    temp_list = []
                    for value in old:
                        new = value.split(inverseby)
                        new = new[1] + " " + new[0]
                        temp_list.append(new)
                    y[field.name] = temp_list
                else:
                    new = old.split(inverseby)
                    new = new[1] + " " + new[0]
                    y[field.name] = new
        if old != y[field.name]:
            one_item = "<b>({})</b> {} --> {} (ID#{})".format(field.label, old, y[field.name], str(y["id"]))
            reporter.append(one_item)
    return reporter

def Substring(collection, field, first, last, allitems):
    first = int(first)
    last = int(last)
    if not first:
        first = None
    if not last:
        last = None
    reporter = []
    for x, y in collection._data.items():
        one_item = ""
        old = y[field.name]
        if allitems:
            old = y[field.name]
            if type(old) is list:
                temp_list = []
                for value in old:
                    new = value[first:last]
                    temp_list.append(new)
                y[field.name] = temp_list
            else:
                new = old[first:last]
                y[field.name] = new
        else:
            if y["id"] in collection._selected_items:
                old = y[field.name]
                if type(old) is list:
                    temp_list = []
                    for value in old:
                        new = value[first:last]
                        temp_list.append(new)
                    y[field.name] = temp_list
                else:
                    new = old[first:last]
                    y[field.name] = new
        if old != y[field.name]:
            one_item = "<b>({})</b> {} --> {} (ID#{})".format(field.label, old, y[field.name], str(y["id"]))
            reporter.append(one_item)
    return reporter