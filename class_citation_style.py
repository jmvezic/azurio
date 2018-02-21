import copy

def simpleStylizer(dictnry, citation):
    dict_to_work = copy.deepcopy(dictnry)
    styled_dict = {}
    for x, y in dict_to_work.items():
        for v, vv in citation.model._name_map.items():
            if vv.is_many:
                if len(y[vv.name]) > 1:
                    y[vv.name] = citation.many_sep.join(y[vv.name][0:-1]) + citation.last_sep + y[vv.name][-1]
                else:
                    y[vv.name] = y[vv.name][0]
        if x not in styled_dict:
            styled_dict[x] = citation.rules.format(**y)

    return styled_dict

def removeextras(syntax, extras):
    #print("OLD:","/"+syntax+"/")
    if syntax[-1] in extras:
        new = syntax[0:-1]
        new = removeextras(new, extras)
        return new
    else:
        #print("NEW:", "/"+syntax+"/")
        return syntax

def newStylizer(collection, citation, numbering):
    try:
        deepdata = copy.deepcopy(collection._data)
        deepgrouping = copy.deepcopy(collection._grouping_index)
        deepfiltering = copy.deepcopy(collection._filtering_index)
        styled_list = []
        global parents
        parents = None
        global previousparent
        previousparent = None

        global item_number
        item_number = 1

        if numbering == 0:  # NO NUMBERING
            pass
        elif numbering == 1:  # GLOBAL NUMBERING
            pass
        elif numbering == 2:  # LOCAL NUMBERING
            pass

        def myprint(d, filters=None):
            def find_key(d, key, value):
                for k, v in d.items():
                    if isinstance(v, dict):
                        p = find_key(v, key, value)
                        if p:
                            return [k] + p
                    elif v == value and k == key:
                        return [k]
            for k, v in sorted(d.items()):
                global parents
                parents = find_key(deepgrouping, k, v)
                global previousparent
                global item_number
                if type(v) is list:
                    if v:
                        if previousparent:
                            comparative = list(set(parents) - set(previousparent))
                            for parent in comparative:
                                stylized_parent = "<h{}>{}</h{}>".format(parents.index(parent)+3, str(parent),parents.index(parent)+3)
                                styled_list.append(stylized_parent)
                        else:
                            for parent in parents:
                                stylized_parent = "<h{}>{}</h{}>".format(parents.index(parent) + 3, str(parent), parents.index(parent) + 3)
                                styled_list.append(stylized_parent)
                        items_in_group = []
                        if numbering == 2:
                            item_number = 1
                        for each in v:
                            if filters and each in filters:
                                item = deepdata[each]
                                item_for_syntax = {}

                                for key, value in item.items():
                                    if value:
                                        if type(value) is list:
                                            if len(value) > 1:
                                                value = "{}{}{}".format(citation.many_sep.join(str(x) for x in value[0:-1]), citation.last_sep, value[-1])
                                                item_for_syntax[key] = value
                                            else:
                                                item_for_syntax[key] = value[0]
                                        else:
                                            item_for_syntax[key] = value
                            elif not filters:
                                item = deepdata[each]
                                item_for_syntax = {}

                                for key, value in item.items():
                                    if value:
                                        if type(value) is list:
                                            if len(value) > 1:
                                                value = "{}{}{}".format(
                                                    citation.many_sep.join(str(x) for x in value[0:-1]),
                                                    citation.last_sep, value[-1])
                                                item_for_syntax[key] = value
                                            else:
                                                item_for_syntax[key] = value[0]
                                        else:
                                            item_for_syntax[key] = value
                            #print(syntax)

                            #print(temp_order)
                            #print(item_for_syntax)

                            syntax = citation.rules[item["type"]].format(**item_for_syntax)

                            nedozvoljeni = [",", ":", ";", "/", ")", " "]
                            syntax = removeextras(syntax, nedozvoljeni)

                            stylized = syntax + "</p>"
                            items_in_group.append(stylized)
                        print(sorted(items_in_group))
                        for eachitem in sorted(items_in_group):
                            if numbering == 1 or numbering == 2:
                                styled_list.append("<p>{}. ".format(str(item_number))+eachitem)
                            else:
                                styled_list.append("<p>"+eachitem)
                            item_number += 1
                            #print(stylized)
                else:
                    if v:
                        myprint(v)
                previousparent = find_key(deepgrouping, k, v)

        if deepgrouping and not deepfiltering:
            myprint(deepgrouping)
        elif deepgrouping and deepfiltering:
            myprint(deepgrouping, filters=collection._filtering_index)
        elif deepfiltering and not deepgrouping:
            items_in_group = []
            for key in deepdata:
                if key in deepfiltering:
                    item = deepdata[key]
                    item_for_syntax = {}

                    for key, value in item.items():
                        if value:
                            if type(value) is list:
                                if len(value) > 1:
                                    value = "{}{}{}".format(citation.many_sep.join(str(x) for x in value[0:-1]), citation.last_sep, value[-1])
                                    item_for_syntax[key] = value
                                else:
                                    item_for_syntax[key] = value[0]
                            else:
                                item_for_syntax[key] = value
                    # print(syntax)

                    # print(temp_order)
                    # print(item_for_syntax)

                    syntax = citation.rules[item["type"]].format(**item_for_syntax)

                    nedozvoljeni = [",", ":", ";", "/", ")", " "]
                    syntax = removeextras(syntax, nedozvoljeni)

                    stylized = syntax + "</p>"
                    items_in_group.append(stylized)
            print(sorted(items_in_group))
            for eachitem in sorted(items_in_group):
                if numbering != 0:
                    styled_list.append("<p>{}. {}".format(str(item_number), eachitem))
                else:
                    styled_list.append("<p>{}".format(eachitem))
                item_number += 1
                # print(stylized)
        elif not deepgrouping and not deepfiltering:
            items_in_group = []
            for key in deepdata:
                item = deepdata[key]
                item_for_syntax = {}

                for key, value in item.items():
                    if value:
                        if type(value) is list:
                            if len(value) > 1:
                                value = "{}{}{}".format(citation.many_sep.join(str(x) for x in value[0:-1]), citation.last_sep, value[-1])
                                item_for_syntax[key] = value
                            else:
                                item_for_syntax[key] = value[0]
                        else:
                            item_for_syntax[key] = value
                # print(syntax)

                # print(temp_order)
                # print(item_for_syntax)

                syntax = citation.rules[item["type"]].format(**item_for_syntax)

                nedozvoljeni = [",", ":", ";", "/", ")", " "]
                syntax = removeextras(syntax, nedozvoljeni)

                stylized = syntax + "</p>"
                items_in_group.append(stylized)
            print(sorted(items_in_group))
            for eachitem in sorted(items_in_group):
                if numbering != 0:
                    styled_list.append("<p>{}. {}".format(str(item_number), eachitem))
                else:
                    styled_list.append("<p>{}".format(eachitem))
                item_number += 1
                # print(stylized)
        return styled_list

    except Exception as e:
        print(e)


class CitationStyle:
    def __init__(self, name, model, rules, stylizer=newStylizer, many_sep="; ", last_sep=" and ", custom=False):
        self.name = name #naziv citatnog stila
        self.model = model #model za citatni stil
        self.rules = rules #lista sintaksi za svaku vrstu publikacije
        self.stylizer = stylizer #funkcija stiliziranja
        self.many_sep = many_sep #graničnik
        self.last_sep = last_sep #zadnji graničnik
        self.custom = custom # custom stil, poput APA, ako je True uzima style.json