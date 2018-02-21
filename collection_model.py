from class_model import DataModel
import json
from datetime import datetime
import copy

import linecache
import sys

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class Collection:
    def __init__(self, model: DataModel):
        # if not model.finalized:
        #     raise Exception('Model not finalized')
        self.model = model
        self._data = {}
        self._recyclebin = {}
        self._current_id = 0  # max(self._data)
        self._saves = []
        self._grouping_index = {}
        self._filtering_index = []
        self._selected_items = []
        self._view_field = "id"
        self._grouping_fields = []

    def TempLoad(self, pos):
        self._data = copy.deepcopy(self._saves[pos]["data"])
        self._recyclebin = copy.deepcopy(self._saves[pos]["recycle"])
        self._current_id = copy.deepcopy(self._saves[pos]["curid"])
        self._grouping_index = copy.deepcopy(self._saves[pos]["group"])
        self._filtering_index = copy.deepcopy(self._saves[pos]["filter"])
        self._selected_items = copy.deepcopy(self._saves[pos]["selected"])
        self._view_field = copy.deepcopy(self._saves[pos]["viewfield"])
        self._grouping_fields = copy.deepcopy(self._saves[pos]["groupfields"])

    def TempSave(self, new=False, pos=None):
        dict_to_save = {
            "data": copy.deepcopy(self._data),
            "recycle": copy.deepcopy(self._recyclebin),
            "curid": self._current_id,
            "group": copy.deepcopy(self._grouping_index),
            "filter": copy.deepcopy(self._filtering_index),
            "selected": copy.deepcopy(self._selected_items),
            "viewfield": self._view_field,
            "groupfields": copy.deepcopy(self._grouping_fields)
        }
        if self._saves:
            if dict_to_save == self._saves[-1]:
                pass
            else:
                if new:
                    self._saves = self._saves[0:pos]
                    self._saves.append(dict_to_save)
                else:
                    self._saves.append(dict_to_save)
        else:
            self._saves.append(dict_to_save)
        # def saveCollectionState(self, name):
        #     curr_date = datetime.now().time()
        #     self._saves["[" + str(curr_date) + "] " + name] = copy.deepcopy(self._data)
        #     # deep copy?
        #
        # def loadCollectionSave(self, savename):
        #     self._data = self._saves.get(savename)

    def PermaSave(self, to_file):
        whole_collection = {}
        whole_collection["model"] = self.model.name
        whole_collection["data"] = self._data
        whole_collection["bin"] = self._recyclebin
        whole_collection["current_id"] = self._current_id
        #whole_collection["point_saves"] = self._saves
        whole_collection["grouping"] = self._grouping_index
        whole_collection["filtering"] = self._filtering_index
        whole_collection["selected"] = self._selected_items
        whole_collection["view_field"] = self._view_field
        with open("saves/" + to_file, 'w') as fp:
            json.dump(whole_collection, fp)

    def NewGrouping(self, fields):
        try:
            params = fields
            self._grouping_fields = params
            group_handler = {}
            listakljuceva = []
            listavrijednosti = []

            i = 0
            for param in params:
                param_names = []
                param_occurences = []
                if self._filtering_index:
                    for x, y in self._data.items():
                        if x in self._filtering_index:
                            if type(y[param]) is list:
                                for e in y[param]:
                                    if e not in param_names:
                                        param_names.append(e)
                            else:
                                if y[param] not in param_names:
                                    param_names.append(y[param])
                else:
                    for x, y in self._data.items():
                        if type(y[param]) is list:
                            for e in y[param]:
                                if e not in param_names:
                                    param_names.append(e)
                        else:
                            if y[param] not in param_names:
                                param_names.append(y[param])
                for name in param_names:
                    temp_occ = []
                    if self._filtering_index:
                        for x, y in self._data.items():
                            if x in self._filtering_index:
                                if type(y[param]) is list:
                                    if name in y[param]:
                                        temp_occ.append(x)
                                else:
                                    if y[param] == name:
                                        temp_occ.append(x)
                        param_occurences.append(temp_occ)
                    else:
                        for x, y in self._data.items():
                            if type(y[param]) is list:
                                if name in y[param]:
                                    temp_occ.append(x)
                            else:
                                if y[param] == name:
                                    temp_occ.append(x)
                        param_occurences.append(temp_occ)
                temp_names = []
                temp_values = []
                for name in param_names:
                    temp_names.append(name)
                    temp_values.append(param_occurences[param_names.index(name)])
                    # group_handler[i][name] = param_occurences[param_names.index(name)]
                listakljuceva.append(temp_names)
                listavrijednosti.append(temp_values)
                i += 1

            def multidict(*args):
                if len(args) == 1:
                    return copy.copy(args[0])
                out = {}
                for x in args[0]:
                    out[x] = multidict(*args[1:])
                return out

            def intersect(*d):
                sets = iter(map(set, d))
                result = sets.next()
                for s in sets:
                    result = result.intersection(s)
                return result

            grouping_index = multidict(*listakljuceva, [])

            result = []
            path = []

            def get_keys(d, target):
                for k, v in d.items():
                    path.append(k)
                    if isinstance(v, dict):
                        get_keys(v, target)
                    if v == target:
                        result.append(copy.copy(path))
                        # print(path)
                    path.pop()

            get_keys(grouping_index, [])
            listaputanja = result

            def find(paths, JSON):
                # print(paths)
                privrem = []
                for each in paths:
                    for e in listakljuceva:
                        for nj in e:
                            if nj == each:
                                opala = listavrijednosti[listakljuceva.index(e)][e.index(nj)]
                                privrem.append(opala)
                # print(privrem)
                data = JSON
                for i in range(0, len(paths)):
                    if type(data[paths[i]]) != list:
                        for x, y in data.items():
                            pass
                        data = data[paths[i]]
                    else:
                        if list(set(privrem[0]).intersection(*privrem)):
                            data[paths[i]] = list(set(privrem[0]).intersection(*privrem))
                        else:
                            del data[paths[i]]

            # print()
            for each in listaputanja:
                find(each, grouping_index)
            self._grouping_index = grouping_index
            print(self._grouping_index)
        except Exception as e:
            print(e)

    def getId(self):
        self._current_id += 1
        return self._current_id

    def SaveToFile(self, file_name):
        with open(file_name, 'w') as fp:
            json.dump(self._data, fp)

    def LoadFile(self, file_name):
        with open(file_name, 'r') as fp:
            self._data = json.load(fp)
        for x, y in self._data.items():
            self._data[int(x)] = self._data.pop(x)

    def validateItem(self, item):
        try:
            ## CHECKS IF ALL MANDATORY FIELDS HAVE VALUES
            fields_to_return = []
            invalid_fields = []
            print(item)
            type_pub = item["type"]
            for x, y in self.model.types.items():
                if y.name == type_pub:
                    mandatory = y.mandatory_atts
                    for m in mandatory:
                        if m.is_many and type(item[m.name]) == list:
                            str_list = list(filter(None, item[m.name]))  # fastest
                            if str_list:
                                pass
                            else:
                                if m not in fields_to_return:
                                    fields_to_return.append(m)

                        else:
                            if item[m.name]:
                                pass
                            else:
                                if m not in fields_to_return:
                                    fields_to_return.append(m)
            #print(fields_to_return)
            ##CHECKS IF VALUES ARE VALID FOR FIELDS THAT HAVE THEM

            for x, y in self.model.types.items():
                if y.name == type_pub:
                    fields_in_type = y.mandatory_atts + y.optional_atts
                    for f in fields_in_type:
                        if f.is_many and type(item[f.name]) == list:
                            pass
                        elif f.is_many and type(item[f.name]) != list:
                            try:
                                item[f.name] = list(item[f.name])
                            except:
                                if f not in invalid_fields:
                                    invalid_fields.append(f)
                        elif f._transform is int:
                            if item[f.name]:
                                try:
                                    transformed = f._transform(item[f.name])
                                    item[f.name] = transformed
                                except Exception as e:
                                    if f not in invalid_fields:
                                        invalid_fields.append(f)
                            else:
                                item[f.name] = None
                        else:
                            try:
                                transformed = f._transform(item[f.name])
                                item[f.name] = transformed
                            except Exception as e:
                                if f not in invalid_fields:
                                    invalid_fields.append(f)

                    for f in fields_in_type:
                        if item[f.name]:
                            pass
                        else:
                            fields_in_type.remove(f)
                    for f in fields_in_type:
                        if f.is_many and type(item[f.name]) == list:
                            temp = []
                            for i in item[f.name]:
                                try:
                                    transformed = f._transform(i)
                                    temp.append(transformed)
                                except Exception as e:
                                    if f not in invalid_fields:
                                        invalid_fields.append(f)
                            item[f.name] = temp
                        else:
                            try:
                                if item[f.name]:
                                    transformed = f._transform(item[f.name])
                                    item[f.name] = transformed
                                else:
                                    item[f.name] = None
                            except Exception as e:
                                if f not in invalid_fields:
                                    invalid_fields.append(f)

            #print(fields_to_return)
            #print(invalid_fields)

            if fields_to_return or invalid_fields:
                faulty_item = item
            else:
                faulty_item = {}

            return fields_to_return, invalid_fields, faulty_item
        except Exception as e:
            PrintException()

    def transformItem(self, item):
        try:
            for x, y in item.items():
                for field in self.model.fields:
                    if field.name == x and field.name != "id" and field.name != "type":
                        if field.is_many:
                            if type(y) != list:
                                item[x] = list(y)
                            else:
                                tempo = []
                                if y:
                                    for each in y:
                                        each = field._transform(each)
                                        tempo.append(each)
                                item[x] = tempo
                        else:
                            if y:
                                item[x] = field._transform(y)
            return item
        except Exception as e:
            print("Transform failed", x, y)
            print(e)
            return item

    def addItem(self, _validate=True, _transform=True, **item):
        # handle id
        id = item.get("id")
        if id is None:
            id = self.getId()
            item["id"] = id
        else:
            if id in self._data:
                raise Exception("Duplicate ID.")
        print(item, "prije transforma")
        if _transform:
            item = self.transformItem(item)
        print(item, "nakon transforma")
        if _validate:
            empty_fields, invalid_fields, faulty = self.validateItem(item)
            if not empty_fields and not invalid_fields:
                self._data[id] = item
            return empty_fields, invalid_fields, faulty
        else:
            self._data[id] = item

    def editItem(self, iden, _validate=True, _transform=True, **item):
        try:
            if _transform:
                item = self.transformItem(item)
            if _validate:
                empty_fields, invalid_fields, faulty = self.validateItem(item)
                if not empty_fields and not invalid_fields:
                    self._data[iden] = item
                return empty_fields, invalid_fields, faulty
            else:
                self._data[iden] = item
        except Exception as e:
            print(e)


    def removeItems(self, ids):
        for id in ids:
            try:
                self._recyclebin[id] = self._data[id]
                del self._data[id]
                if self._grouping_index:
                    self.NewGrouping(self._grouping_fields)
            except Exception as e:
                print(e)

    def restoreItems(self, ids):
        for id in ids:
            try:
                self._data[id] = self._recyclebin[id]
                del self._recyclebin[id]
                if self._grouping_index:
                    self.NewGrouping(self._grouping_fields)
            except:
                raise Exception("Couldn't restore the item (ID error)")

    def permaDelete(self, ids):
        for id in ids:
            try:
                del self._recyclebin[id]
            except:
                raise Exception("Error in perma deleting")

    def addBibtexFile(self, path):
        pass

    def genItems(self, flt=None):
        if flt:
            for item in filter(flt, self._data.values()):
                yield item
        else:
            for item in self._data.values():
                yield item

    def genIDs(self, flt=None):
        id_name = self.model.id.name
        if flt:
            for item in filter(flt, self._data.values()):
                yield item[id_name]
        else:
            for item in self._data.values():
                yield item[id_name]

    def saveCollectionState(self, name):
        curr_date = datetime.now().time()
        self._saves["[" + str(curr_date) + "] " + name] = copy.deepcopy(self._data)
        # deep copy?

    def loadCollectionSave(self, savename):
        self._data = self._saves.get(savename)

    def filterCollection(self, filterdict):
        plus = "+"
        minus = "-"
        equal = "="

        filtered_list = []

        for x, y in self._data.items():
            to_filters = []
            for a, b in filterdict.items():
                if b["type"] is int:
                    if type(y[b["field"]]) is list:
                        for each in y[b["field"]]:
                            if b["operator"] is plus:
                                if each > b["value"]:
                                    to_filters.append(True)
                                else:
                                    to_filters.append(False)
                            elif b["operator"] is minus:
                                if each < b["value"]:
                                    to_filters.append(True)
                                else:
                                    to_filters.append(False)
                            elif b["operator"] is equal:
                                if each == b["value"]:
                                    to_filters.append(True)
                                else:
                                    to_filters.append(False)
                    else:
                        if b["operator"] is plus:
                            if y[b["field"]] > b["value"]:
                                to_filters.append(True)
                            else:
                                to_filters.append(False)
                        elif b["operator"] is minus:
                            if y[b["field"]] < b["value"]:
                                to_filters.append(True)
                            else:
                                to_filters.append(False)
                        elif b["operator"] is equal:
                            if y[b["field"]] == b["value"]:
                                to_filters.append(True)
                            else:
                                to_filters.append(False)
                else:
                    if type(y[b["field"]]) is list:
                        for each in y[b["field"]]:
                            if b["operator"] is plus:
                                if b["value"] in each:
                                    to_filters.append(True)
                                else:
                                    to_filters.append(False)
                            elif b["operator"] is minus:
                                if b["value"] not in each:
                                    to_filters.append(True)
                                else:
                                    to_filters.append(False)
                            elif b["value"] == y[b["field"]]:
                                if y[b["field"]] == each:
                                    to_filters.append(True)
                                else:
                                    to_filters.append(False)
                    else:
                        if b["operator"] is plus:
                            if b["value"] in y[b["field"]]:
                                to_filters.append(True)
                            else:
                                to_filters.append(False)
                        elif b["operator"] is minus:
                            if b["value"] not in y[b["field"]]:
                                to_filters.append(True)
                            else:
                                to_filters.append(False)
                        elif b["value"] == y[b["field"]]:
                            if y[b["field"]] == b["value"]:
                                to_filters.append(True)
                            else:
                                to_filters.append(False)
            if False not in to_filters:
                print(to_filters)
                filtered_list.append(x)
        self._filtering_index = filtered_list
        if self._grouping_index:
            self.NewGrouping(self._grouping_fields)


        # self.saveCollectionState("Save before filter: ({}: {})".format(field, value))
        # filtered_dict = {}
        # if field is None or value is None:
        #     pass
        # else:
        #     for z, y in self._data.items():
        #         for a, b in y.items():
        #             if isinstance(b, (list, tuple)):
        #                 try:
        #                     if value in b:
        #                         filtered_dict[z] = y
        #                     else:
        #                         continue
        #                 except:
        #                     continue
        #             else:
        #                 try:
        #                     if value == b:
        #                         filtered_dict[z] = y
        #                     else:
        #                         continue
        #                 except:
        #                     continue
        #     self._data = filtered_dict
        # self.saveCollectionState("Save after filter: ({}: {})".format(field, value))

    def groupCollection(self, groupby):
        self.saveCollectionState("Save before grouping: ({})".format(groupby))
        working_dict = copy.deepcopy(self._data)
        dict_values = {}
        dict_index = {}
        multis = {}
        multis_index = {}
        empty_info = "### No information ###"
        for unit in working_dict:
            if type(working_dict[unit][groupby]) is list:
                working_dict[unit][groupby] = list(filter(None, working_dict[unit][groupby]))
                if not working_dict[unit][groupby]:
                    x = empty_info
                    if x in multis:
                        multis[x]["count"] += 1
                        multis_index[x].add(unit)
                    else:
                        multis[x] = {
                            "count": 1
                        }
                        multis_index[x] = {unit}
                    self._grouping_index = multis_index.copy()
                else:
                    for x in working_dict[unit][groupby]:
                        if x in multis:
                            multis[x]["count"] += 1
                            multis_index[x].add(unit)
                        else:
                            multis[x] = {
                                "count": 1
                            }
                            multis_index[x] = {unit}
                    self._grouping_index = multis_index.copy()
            else:
                byvalue = working_dict[unit][groupby]
                if not byvalue:
                    byvalue = empty_info
                    if byvalue in dict_values:
                        dict_values[byvalue]["count"] += 1
                        dict_index[byvalue].add(unit)
                    else:
                        dict_values[byvalue] = {
                            "count": 1
                        }
                        dict_index[byvalue] = {unit}
                        self._grouping_index = dict_index.copy()
                else:
                    if byvalue in dict_values:
                        dict_values[byvalue]["count"] += 1
                        dict_index[byvalue].add(unit)
                    else:
                        dict_values[byvalue] = {
                            "count": 1
                        }
                        dict_index[byvalue] = {unit}
                        self._grouping_index = dict_index.copy()
        self.saveCollectionState("Save after grouping: ({})".format(groupby))