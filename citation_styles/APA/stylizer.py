import copy
import json


def removeextras(syntax, extras):
    #print("OLD:","/"+syntax+"/")
    if syntax[-1] in extras:
        new = syntax[0:-1]
        new = removeextras(new, extras)
        return new
    else:
        #print("NEW:", "/"+syntax+"/")
        return syntax

def NewAPAStylize(collection, citation, numbering):
    try:
        deepdata = copy.deepcopy(collection._data)
        deepgrouping = copy.deepcopy(collection._grouping_index)
        deepfiltering = copy.deepcopy(collection._filtering_index)
        styled_list = []
        global parents
        parents = None
        global previousparent
        previousparent = None
        global mapper
        with open('models/{}/cit_mappers/APA.json'.format(collection.model.name), 'r') as fp:
            mapper = json.load(fp)

        global item_number
        item_number = 1

        if numbering == 0: #NO NUMBERING
            pass
        elif numbering == 1: #GLOBAL NUMBERING
            pass
        elif numbering == 2: #LOCAL NUMBERING
            pass

        def myprint(d):
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
                            if deepfiltering and each in deepfiltering:
                                item = deepdata[each]
                                apa_type = ""
                                for apatype, modeltype in mapper["type_maps"].items():
                                    if modeltype == item["type"]:
                                        apa_type = apatype
                                apa_temp_order = citation.rules["Types"][apa_type]
                                fixed_apa_order = []
                                model_temp_order = []
                                for apa_field in apa_temp_order:
                                    if apa_field in mapper["field_maps"]:
                                        if mapper["field_maps"][apa_field] in item:
                                            if item[mapper["field_maps"][apa_field]]:
                                                model_temp_order.append(mapper["field_maps"][apa_field])
                                                fixed_apa_order.append(apa_field)
                                # print(model_temp_order)
                                # print(fixed_apa_order)
                                syntax = ""
                                for each in fixed_apa_order:
                                    syntax += citation.rules["Fields"][each]
                                # print(syntax)
                                for fapa in fixed_apa_order:
                                    syntax = syntax.replace(fapa, model_temp_order[fixed_apa_order.index(fapa)])
                                item_for_syntax = {}
                                for key, value in item.items():
                                    if key in model_temp_order:
                                        if type(value) is list:
                                            if len(value) > 1:
                                                value = "{}{}{}".format(
                                                    citation.rules["many_sep"].join(str(x) for x in value[0:-1]),
                                                    citation.rules["last_sep"], value[-1])
                                                item_for_syntax[key] = value
                                            else:
                                                item_for_syntax[key] = value[0]
                                        else:
                                            item_for_syntax[key] = value
                                # print(syntax)

                                # print(temp_order)
                                # print(item_for_syntax)

                                nedozvoljeni = [",", ":", ";", "/", ")", " "]
                                syntax = removeextras(syntax, nedozvoljeni)

                                stylized = "{}</p>".format(syntax.format(**item_for_syntax))
                                items_in_group.append(stylized)
                            else:
                                item = deepdata[each]
                                apa_type = ""
                                for apatype, modeltype in mapper["type_maps"].items():
                                    if modeltype == item["type"]:
                                        apa_type = apatype
                                apa_temp_order = citation.rules["Types"][apa_type]
                                fixed_apa_order = []
                                model_temp_order = []
                                for apa_field in apa_temp_order:
                                    if apa_field in mapper["field_maps"]:
                                        if mapper["field_maps"][apa_field] in item:
                                            if item[mapper["field_maps"][apa_field]]:
                                                model_temp_order.append(mapper["field_maps"][apa_field])
                                                fixed_apa_order.append(apa_field)
                                #print(model_temp_order)
                                #print(fixed_apa_order)
                                syntax = ""
                                for each in fixed_apa_order:
                                    syntax += citation.rules["Fields"][each]
                                #print(syntax)
                                for fapa in fixed_apa_order:
                                    syntax = syntax.replace(fapa, model_temp_order[fixed_apa_order.index(fapa)])
                                item_for_syntax = {}
                                for key, value in item.items():
                                    if key in model_temp_order:
                                        if type(value) is list:
                                            if len(value) > 1:
                                                value = "{}{}{}".format(citation.rules["many_sep"].join(str(x) for x in value[0:-1]), citation.rules["last_sep"], value[-1])
                                                item_for_syntax[key] = value
                                            else:
                                                item_for_syntax[key] = value[0]
                                        else:
                                            item_for_syntax[key] = value
                                #print(syntax)

                                #print(temp_order)
                                #print(item_for_syntax)

                                nedozvoljeni = [",", ":", ";", "/", ")", " "]
                                syntax = removeextras(syntax, nedozvoljeni)

                                stylized = "{}</p>".format(syntax.format(**item_for_syntax))
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

        if deepgrouping or (deepfiltering and deepgrouping):
            myprint(deepgrouping)
        elif deepfiltering and not deepgrouping:
            items_in_group = []
            for key in deepdata:
                if key in deepfiltering:
                    item = deepdata[key]
                    apa_type = ""
                    for apatype, modeltype in mapper["type_maps"].items():
                        if modeltype == item["type"]:
                            apa_type = apatype
                    apa_temp_order = citation.rules["Types"][apa_type]
                    fixed_apa_order = []
                    model_temp_order = []
                    for apa_field in apa_temp_order:
                        if apa_field in mapper["field_maps"]:
                            if mapper["field_maps"][apa_field] in item:
                                if item[mapper["field_maps"][apa_field]]:
                                    model_temp_order.append(mapper["field_maps"][apa_field])
                                    fixed_apa_order.append(apa_field)
                    # print(model_temp_order)
                    # print(fixed_apa_order)
                    syntax = ""
                    for each in fixed_apa_order:
                        syntax += citation.rules["Fields"][each]
                    # print(syntax)
                    for fapa in fixed_apa_order:
                        syntax = syntax.replace(fapa, model_temp_order[fixed_apa_order.index(fapa)])
                    item_for_syntax = {}
                    for key, value in item.items():
                        if key in model_temp_order:
                            if type(value) is list:
                                if len(value) > 1:
                                    value = "{}{}{}".format(citation.rules["many_sep"].join(str(x) for x in value[0:-1]),
                                                            citation.rules["last_sep"], value[-1])
                                    item_for_syntax[key] = value
                                else:
                                    item_for_syntax[key] = value[0]
                            else:
                                item_for_syntax[key] = value
                    # print(syntax)

                    # print(temp_order)
                    # print(item_for_syntax)

                    nedozvoljeni = [",", ":", ";", "/", ")", " "]
                    syntax = removeextras(syntax, nedozvoljeni)

                    stylized = "{}</p>".format(syntax.format(**item_for_syntax))
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
                apa_type = ""
                for apatype, modeltype in mapper["type_maps"].items():
                    if modeltype == item["type"]:
                        apa_type = apatype
                apa_temp_order = citation.rules["Types"][apa_type]
                fixed_apa_order = []
                model_temp_order = []
                for apa_field in apa_temp_order:
                    if apa_field in mapper["field_maps"]:
                        if mapper["field_maps"][apa_field] in item:
                            if item[mapper["field_maps"][apa_field]]:
                                model_temp_order.append(mapper["field_maps"][apa_field])
                                fixed_apa_order.append(apa_field)
                # print(model_temp_order)
                # print(fixed_apa_order)
                syntax = ""
                for each in fixed_apa_order:
                    syntax += citation.rules["Fields"][each]
                # print(syntax)
                for fapa in fixed_apa_order:
                    syntax = syntax.replace(fapa, model_temp_order[fixed_apa_order.index(fapa)])
                item_for_syntax = {}
                for key, value in item.items():
                    if key in model_temp_order:
                        if type(value) is list:
                            if len(value) > 1:
                                value = "{}{}{}".format(citation.rules["many_sep"].join(str(x) for x in value[0:-1]), citation.rules["last_sep"], value[-1])
                                item_for_syntax[key] = value
                            else:
                                item_for_syntax[key] = value[0]
                        else:
                            item_for_syntax[key] = value
                # print(syntax)

                # print(temp_order)
                # print(item_for_syntax)

                nedozvoljeni = [",", ":", ";", "/", ")", " "]
                syntax = removeextras(syntax, nedozvoljeni)

                stylized = "{}</p>".format(syntax.format(**item_for_syntax))
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

def APAstylize(collection, citationstyle):
    pass
    #
    # try:
    #     # citationstyle.rules: x, y gdje je x vrsta publikacije, y sintaksa
    #     # citationstyle.model: objekt modela
    #     # citationstyle.many_sep: graničnik
    #     # citationstyle.last_sep: zadnji graničnik
    #     deepdata = copy.deepcopy(collection._data)
    #     deepgrouping = copy.deepcopy(collection._grouping_index)
    #     deepfiltering = copy.deepcopy(collection._filtering_index)
    #     styled_list = []
    #     #previousparent = None
    #     item_counter = 1
    #
    #     def myprint(d, previousparent=None, item_counter=1):
    #         def find_key(d, key, value):
    #             for k, v in d.items():
    #                 if isinstance(v, dict):
    #                     p = find_key(v, key, value)
    #                     if p:
    #                         return [k] + p
    #                 elif v == value and k == key:
    #                     return [k]
    #
    #         for k, v in sorted(d.items()):
    #             parents = find_key(deepgrouping, k, v)
    #             if type(v) is list:
    #                 if v:
    #                     if previousparent:
    #                         comparative = list(set(parents) - set(previousparent))
    #                         for parent in comparative:
    #                             labelo = "<h{}>{}</h{}>".format(parents.index(parent) + 3, str(parent), parents.index(parent) + 3)
    #                             styled_list.append(labelo)
    #                     else:
    #                         for parent in parents:
    #                             labelo = "<h{}>{}</h{}>".format(parents.index(parent) + 3, str(parent), parents.index(parent) + 3)
    #                             styled_list.append(labelo)
    #                     for each in v:
    #                         for x, y in deepdata.items():
    #                             if y["id"] == each:
    #                                 for field in citationstyle.model.fields:
    #                                     if field.is_many:
    #                                         if len(y[field.name]) > 1:
    #                                             try:
    #                                                 y[field.name] = citationstyle.many_sep.join(
    #                                                     y[field.name][0:-1]) + citationstyle.last_sep + y[field.name][
    #                                                                     -1]
    #                                             except Exception as e:
    #                                                 print(e, y[field.name], "ID1")
    #                                         else:
    #                                             if y[field.name]:
    #                                                 try:
    #                                                     y[field.name] = y[field.name][0]
    #                                                 except Exception as e:
    #                                                     print(e, y["id"], "ID2")
    #                                 stylesyntax = ""
    #                                 with open("models/{}/cit_mappers/APA.json".format(citationstyle.model.name),
    #                                           'r') as fp:
    #                                     mapper = json.load(fp)
    #                                 temp_syntax = ""
    #                                 if y["type"] in mapper["type_maps"].values():
    #                                     gettype = ""
    #                                     for tt, gg in mapper["type_maps"].items():
    #                                         if y["type"] == gg:
    #                                             gettype = tt
    #                                     for each in citationstyle.rules["Types"][gettype]:
    #                                         if each in mapper["field_maps"].keys():
    #                                             temp_syntax += citationstyle.rules["Fields"][each]
    #                                 nedozvoljeni = [",", ":", ";", "/", ")", " "]
    #                                 temp_syntax = removeextras(temp_syntax, nedozvoljeni)
    #                                 #print(temp_syntax)
    #                                 for bla, nja in mapper["field_maps"].items():
    #                                     temp_syntax = temp_syntax.replace(bla, nja)
    #                                 styled_list.append("<p>{}. ".format(item_counter) + temp_syntax.format(**y) + "</p>")
    #                                 item_counter+=1
    #             else:
    #                 if v:
    #                     myprint(v)
    #             previousparent = find_key(deepgrouping, k, v)
    #
    #     # BEZ GRUPIRANJA I FILTRIRANJA
    #     if not deepgrouping and not deepfiltering:
    #         for x, y in deepdata.items():
    #             for field in citationstyle.model.fields:
    #                 if field.is_many:
    #                     if len(y[field.name]) > 1:
    #                         try:
    #                             y[field.name] = citationstyle.many_sep.join(y[field.name][0:-1]) + citationstyle.last_sep + y[field.name][-1]
    #                         except Exception as e:
    #                             print(e, y[field.name])
    #                     else:
    #                         try:
    #                             y[field.name] = y[field.name][0]
    #                         except Exception as e:
    #                             print(e, y["id"])
    #             stylesyntax = ""
    #             with open("models/{}/cit_mappers/APA.json".format(citationstyle.model.name), 'r') as fp:
    #                 mapper = json.load(fp)
    #             temp_syntax = ""
    #             if y["type"] in mapper["type_maps"].values():
    #                 gettype = ""
    #                 for tt, gg in mapper["type_maps"].items():
    #                     if y["type"] == gg:
    #                         gettype = tt
    #                 for each in citationstyle.rules["Types"][gettype]:
    #                     if each in mapper["field_maps"].keys():
    #                         temp_syntax += citationstyle.rules["Fields"][each]
    #             nedozvoljeni = [",", ":", ";", "/", ")", " "]
    #             temp_syntax = removeextras(temp_syntax, nedozvoljeni)
    #             #print(temp_syntax)
    #             for bla, nja in mapper["field_maps"].items():
    #                 temp_syntax = temp_syntax.replace(bla, nja)
    #             styled_list.append("<p>{}. ".format(item_counter)+temp_syntax.format(**y)+"</p>")
    #             item_counter += 1
    #     elif deepgrouping and not deepfiltering:
    #         myprint(deepgrouping)
    #
    #     return styled_list
    #
    # except Exception as e:
    #     raise Exception(e)