import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from languages import translations
from settings import *
import ctypes
from class_model import *
import loaded_models
from loaded_models import models
from save_model_to_json import SaveToJson
from functools import partial
from collection_model import *
from themes import LoadThemes
import json
import copy
import os
import imp
import csv
import codecs
import formats.CSV.mapper_function
import formats.BibTeX.mapper_function
import formats.MARC.mapper_function
import additional_functions
import achievements
import datetime
import class_citation_style
import class_bibliography

myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
#ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        menu = QtWidgets.QMenu(parent)
        exitAction = menu.addAction(translations["SystemTrayExit"][parent.language])
        exitAction.triggered.connect(parent.close)
        self.setContextMenu(menu)

class Azurio(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        #self.showMaximized()

    def closeEvent(self, *args, **kwargs):
        self.tray_icon.hide()

    def ApplyStylesheet(self, preview=False, previewNew=False):
        self.themes_dict = LoadThemes()
        if preview:
            self.background_color = self.themes_dict[self.previewtheme]["BackgroundColor"]
            self.foreground_color = self.themes_dict[self.previewtheme]["ForegroundColor"]
            self.highlight_color = self.themes_dict[self.previewtheme]["HighlightColor"]
            self.highlighted_text_color = self.themes_dict[self.previewtheme]["HighlightedTextColor"]
            self.border_color = self.themes_dict[self.previewtheme]["BorderColor"]
            self.accent_color = self.themes_dict[self.previewtheme]["AccentColor"]
            self.warning_color = self.themes_dict[self.previewtheme]["WarningColor"]
        elif previewNew:
            self.background_color = self.new_theme_to_preview["BackgroundColor"]
            self.foreground_color = self.new_theme_to_preview["ForegroundColor"]
            self.highlight_color = self.new_theme_to_preview["HighlightColor"]
            self.highlighted_text_color = self.new_theme_to_preview["HighlightedTextColor"]
            self.border_color = self.new_theme_to_preview["BorderColor"]
            self.accent_color = self.new_theme_to_preview["AccentColor"]
            self.warning_color = self.new_theme_to_preview["WarningColor"]
        else:
            self.background_color = self.themes_dict[self.theme]["BackgroundColor"]
            self.foreground_color = self.themes_dict[self.theme]["ForegroundColor"]
            self.highlight_color = self.themes_dict[self.theme]["HighlightColor"]
            self.highlighted_text_color = self.themes_dict[self.theme]["HighlightedTextColor"]
            self.border_color = self.themes_dict[self.theme]["BorderColor"]
            self.accent_color = self.themes_dict[self.theme]["AccentColor"]
            self.warning_color = self.themes_dict[self.theme]["WarningColor"]
        self.fontsize = 10
        self.stylesheet_to_use = '* {font-size: ' + str(
            self.fontsize) + 'pt;color:' + self.foreground_color + ';background-color:' + self.background_color + ';} QMenuBar::item{background-color:' + self.background_color + ';} QMenuBar::item::selected,QMenu::item::selected{background-color:' + self.highlight_color + ';color:' + self.highlighted_text_color + '} QPushButton {border:1px solid ' + self.border_color + ';padding:5px;}QPushButton::hover {border:1px solid ' + self.highlight_color + ';background-color:' + self.highlight_color + ';color:' + self.highlighted_text_color + ';} QPushButton:focus{border:1px solid ' + self.accent_color + '}' + "QPushButton::disabled{color:"+self.border_color+";}" + "QLineEdit,QTextEdit{background-color:" + self.background_color + ";padding:5px;margin:2px;border-radius:2px;border:1px solid " + self.border_color + ";} QLineEdit:disabled,QTextEdit:disabled{border:0;} QLineEdit:focus,QTextEdit:focus{border:1px solid " + self.accent_color + ";} QComboBox {border:1px solid " + self.border_color + ";padding:5px 7px 5px 7px;border-radius:2px;} QComboBox:hover{border:1px solid " + self.accent_color + "} QComboBox:focus{border:1px solid " + self.accent_color + "} QComboBox:disabled{border:0;} QComboBox::drop-down{border-width:1px;} QComboBox::down-arrow{image: url(downarrow.png);} QAbstractItemView{selection-background-color:" + self.accent_color + ";selection-color:" + self.highlighted_text_color + ";}" + "QTabBar::tab{background-color:"+self.foreground_color+";color:"+self.background_color+";margin:0 3px 0 3px;padding:6px;} QTabBar::tab:selected{background-color:"+self.accent_color+";} QTabWidget::pane{border:1px solid "+self.border_color+"} QTabBar::tab:hover{background-color:"+self.accent_color+";}"
        self.setStyleSheet(self.stylesheet_to_use)
        self.color_scheme_to_apply = 'QMenu::item,QMenu::QAction,QMenu{background-color:' + self.background_color + ';color:' + self.foreground_color + '} QMenuBar::item::selected,QMenu::item::selected{background-color:' + self.highlight_color + ';color:' + self.highlighted_text_color + '}'

    def ApplyStylesheetToMenus(self):
        try:
            self.models_menu_copy_model.setStyleSheet(self.color_scheme_to_apply)
            self.models_menu_default.setStyleSheet(self.color_scheme_to_apply)
            self.col_menu_new_col.setStyleSheet(self.color_scheme_to_apply)
            self.GroupingOptionsMenu.setStyleSheet(self.color_scheme_to_apply)
        except Exception as e:
            print(e)

    def initUI(self):
        self.settings = LoadSettings()
        self.theme = self.settings["theme"]
        self.transparent_background = "background-color:rgba(0,0,0,0);"
        self.status = self.statusBar()
        #print(settings)
        self.language = self.settings["lang"]
        self.set_model = self.settings["default_model"]
        self.collection_view_field = "id"
        #self.iconfile = "Tw2_sign_aard.png"
        self.checkboxes_handler = {}
        self.collections = {}
        self.OpenSavedCollectionsMetadata()

        self.ApplyStylesheet()

        _translate = QtCore.QCoreApplication.translate

        self.grid = QGridLayout()
        self.grid.setSpacing(0)

        self.setLayout(self.grid)

        self.mainwidget = QWidget()

        self.mainMenu = self.menuBar()
        self.col_menu = self.mainMenu.addMenu(translations["MainMenuCollection"][self.language])
        self.models_menu = self.mainMenu.addMenu(translations["MainMenuModels"][self.language])
        self.styles_menu = self.mainMenu.addMenu(translations["MainMenuCitationStyles"][self.language])
        self.mappings_menu = self.mainMenu.addMenu(translations["MainMenuMappings"][self.language])
        self.OpBibl = QAction(translations["MainMenuBibliography"][self.language], self)
        self.OpBibl.setShortcut("Ctrl+Shift+B")
        self.MainMenuBibliography = self.mainMenu.addAction(self.OpBibl)
        self.OpBibl.triggered.connect(self.BibliographyWindow)
        self.settings_menu = self.mainMenu.addMenu(translations["MainMenuSettings"][self.language])
        #self.help_menu = self.mainMenu.addMenu(translations["MainMenuHelp"][self.language])

        self.models_menu_new_model = QAction(translations["MainMenuModelsNewModel"][self.language], self)
        #self.models_menu_default_model = QAction(translations["MainMenuModelsChooseDefaultModel"][self.language], self)
        self.models_menu_new_model.setShortcut("Ctrl+M")
        self.models_menu_new_model.triggered.connect(self.NewModelOpenWindow)
        self.models_menu.addAction(self.models_menu_new_model)
        #self.models_menu.addAction(self.models_menu_copy_model)
        self.models_menu_copy_model = QMenu(translations["MainMenuModelsCopyModel"][self.language])
        self.models_menu_copy_model.setStyleSheet(self.color_scheme_to_apply)
        for x,y in models.items():
            action = QAction(x,self)
            #action = self.models_menu_copy_model.addAction(x)
            self.models_menu_copy_model.addAction(action)
            action.triggered.connect(partial(self.NewModelOpenWindow,model=x))
        self.models_menu.addMenu(self.models_menu_copy_model)

        self.models_menu_default = QMenu(translations["MainMenuModelsChooseDefaultModel"][self.language])
        self.models_menu_default.setStyleSheet(self.color_scheme_to_apply)
        for x,y in models.items():
            if x != self.set_model:
                action = self.models_menu_default.addAction(x)
                action.triggered.connect(partial(self.setDefaultModel,model=x))
            else:
                action = self.models_menu_default.addAction(x + " "+ translations["MainMenuChooseDefaultModelIsDefault"][self.language])

        self.models_menu.addMenu(self.models_menu_default)


        self.col_menu_new_col = QMenu(translations["MainMenuCollectionNewCollection"][self.language])
        self.col_menu_new_col.setStyleSheet(self.color_scheme_to_apply)
        for x,y in models.items():
            if x == self.set_model:
                action = self.col_menu_new_col.addAction(x + " "+ translations["MainMenuChooseDefaultModelIsDefault"][self.language])
                action.setShortcut("Ctrl+N")
                action.triggered.connect(partial(self.NewCollection,model=x))
        for x,y in models.items():
            if x != self.set_model:
                action = self.col_menu_new_col.addAction(x)
                action.triggered.connect(partial(self.NewCollection, model=x))

        self.col_menu.addMenu(self.col_menu_new_col)

        self.col_menu_save_col = QAction(translations["MainMenuCollectionSaveCollection"][self.language], self)
        self.col_menu_save_col.setShortcut("Ctrl+S")
        self.col_menu_save_col.triggered.connect(self.PermaSaveWindow)
        self.col_menu.addAction(self.col_menu_save_col)

        # self.col_menu_new_col = QAction(translations["MainMenuCollectionNewCollection"][self.language], self)
        self.col_menu_edit_col = QAction(translations["MainMenuCollectionEditCollection"][self.language], self)
        self.col_menu_edit_col.setShortcut("Ctrl+E")
        self.col_menu_edit_col.triggered.connect(self.OpenCollectionWindow)
        # self.col_menu.addAction(self.col_menu_new_col)
        self.col_menu.addAction(self.col_menu_edit_col)


        self.styles_menu_new_style = QAction(translations["MainMenuCitationStylesNewCitationStyle"][self.language], self)
        self.styles_menu_new_style.triggered.connect(self.NewStyleWindow)
        self.styles_menu_new_style.setShortcut("Shift+C")

        self.styles_menu_edit_style = QMenu(translations["MainMenuCitationStylesEditCitationStyle"][self.language])

        self.styles_menu_default_style = QMenu(translations["MainMenuCitationStylesChooseDefaultStyle"][self.language], self)
        self.styles_menu.addAction(self.styles_menu_new_style)
        self.styles_menu.addMenu(self.styles_menu_edit_style)
        self.styles_menu.addMenu(self.styles_menu_default_style)
        self.styles_menu_default_style.addAction("APA ({})".format(translations["DefaultStyle"][self.language]))

        formats_list = []
        for root, dirs, files in os.walk("formats/"):
            for dir in dirs:
                formats_list.append(dir)
        print(formats_list)

        self.mappings_menu_map_formats = QMenu(translations["MainMenuMappingsFormats"][self.language], self)

        for format in formats_list:
            if format != "__pycache__":
                format_action = self.mappings_menu_map_formats.addAction(format)
                format_action.triggered.connect(partial(self.FormatMapperHandler, format))

        self.mappings_menu_map_styles = QMenu(translations["MainMenuMappingsCitationStyles"][self.language], self)
        self.mappings_menu.addMenu(self.mappings_menu_map_formats)
        self.mappings_menu.addMenu(self.mappings_menu_map_styles)

        styles_list = []
        for root, dirs, files in os.walk("citation_styles/"):
            for dir in dirs:
                styles_list.append(dir)
        print(styles_list)

        for style in styles_list:
            if style != "__pycache__":
                style_action = self.mappings_menu_map_styles.addAction(style)
                style_action.triggered.connect(partial(self.StylesMapperHandler, style))

        self.settings_menu_appereance = QAction(translations["MainMenuSettingsEditAppereance"][self.language], self)
        self.settings_menu_appereance.setShortcut("Ctrl+P")
        self.settings_menu_appereance.triggered.connect(self.AppereanceWindow)
        self.settings_menu_choose_language = QAction(translations["MainMenuSettingsChooseLanguage"][self.language], self)
        self.settings_menu_new_language = QAction(translations["MainMenuSettingsAddLanguage"][self.language], self)
        self.settings_menu.addAction(self.settings_menu_appereance)
        self.settings_menu.addAction(self.settings_menu_choose_language)
        self.settings_menu.addAction(self.settings_menu_new_language)

        self.welcomeLabel = QLabel(_translate("MainWindow",
                                              "<html><head/><body><p align=\"center\"><img src='logo_back_transparent.png'  /></p></body></html>"))

        self.setCentralWidget(self.mainwidget)
        self.mainwidget.setLayout(self.grid)
        self.grid.addWidget(self.welcomeLabel, 0, 0, 1, 2)

        self.resize(900, 600)
        self.setWindowTitle(self.settings["name"] + " " + self.settings["version"])

        app_icon = QtGui.QIcon()
        app_icon.addFile('logo_back_transparent.png', QtCore.QSize(256, 256))
        app.setWindowIcon(app_icon)

        self.center()
        self.show()


        self.tray_icon = SystemTrayIcon(app_icon, self)
        self.tray_icon.show()

        models_count = 0
        for x,y in models.items():
            models_count += 1

        self.status.showMessage(self.settings["name"] + " " + self.settings["version"] + " " + translations["LoadedStatusInfo"][self.language])

        self.mainwidget.setStyleSheet("* {margin:2px;padding:15px;}")

        self.all_models_panel = QFrame()
        self.all_models_panel.setFrameStyle(QFrame.StyledPanel)
        self.all_models_panel.setStyleSheet(self.transparent_background)
        self.grid.addWidget(self.all_models_panel, 0, 0)

        self.default_model_panel = QFrame()
        self.default_model_panel.setFrameStyle(QFrame.StyledPanel)
        self.default_model_panel.setStyleSheet(self.transparent_background)
        self.grid.addWidget(self.default_model_panel, 0, 1)


        ## PRIKAZ MODELA

        self.CheckIfModels()

        self.StyleModelMenus = []
        self.LoadCitationStyles()
        self.RefreshEditStyleMenu()

    def CheckIfModels(self):
        list_of_models = []
        for x,y in models.items():
            list_of_models.append(x)
        list_of_models_for_display = "<br>".join(list_of_models)

        if list_of_models:

            self.all_models_label = QLabel("<p><h3>" + translations["AllModelsPanelText"][self.language] +"</h3><h1>"+str(len(list_of_models))+"</h1>"+list_of_models_for_display+"</p>")
            self.all_models_label.setAlignment(QtCore.Qt.AlignCenter)
            self.all_models_label.setStyleSheet(self.transparent_background)
            self.grid.addWidget(self.all_models_label, 0, 0)

            types_for_model_panel = []
            fields_in_types = []
            model_object = models[self.set_model]["object"]
            for x,y in model_object.types.items():
                types_for_model_panel.append(x)
                tempr_list = []
                for b in y.mandatory_atts:
                    if b.name != "id" and b.name != "type":
                        tempr = b.label + " (" + translations["DefaultModelMandatoryText"][self.language] + ")"
                        tempr_list.append(tempr)

                for b in y.optional_atts:
                    tempr = b.label
                    tempr_list.append(tempr)
                fields_in_types.append(tempr_list)
            #print(types_for_model_panel)
            #print(fields_in_types)

            ij = 0
            strings_to_display = []
            for x in types_for_model_panel:
                string_to_display = ""
                fields_to_display = "<br>".join(fields_in_types[ij])
                string_to_display = "<u><b>"+x+"</b></u><br>"+fields_to_display
                strings_to_display.append(string_to_display)
                ij+=1

            strings_to_display = "<br>".join(strings_to_display)
            #print(strings_to_display)

            self.default_model_label = QLabel("<p><h3>" + translations["DefaultModelInfo"][self.language] +"</h3><h1>"+self.set_model+"</h1>"+strings_to_display+"</p>")
            self.default_model_label.setStyleSheet("word-wrap:break-word;")
            self.default_model_label.setAlignment(QtCore.Qt.AlignCenter)
            self.default_model_label.setStyleSheet(self.transparent_background)
            self.grid.addWidget(self.default_model_label, 0, 1)

        else:
            self.all_models_panel.hide()
            self.default_model_panel.hide()
            self.no_models_label = QLabel("<b>"+translations["NoModelsLabel"][self.language]+"</b>")
            self.grid.addWidget(self.no_models_label, 0, 0)

    def RefreshDefaultModelMenu(self):
        self.models_menu_default.clear()
        for x,y in models.items():
            if x != self.set_model:
                action = self.models_menu_default.addAction(x)
                action.triggered.connect(partial(self.setDefaultModel,model=x))
            else:
                action = self.models_menu_default.addAction(x + " "+ translations["MainMenuChooseDefaultModelIsDefault"][self.language])

    def RefreshDefaultModelInfo(self):
        types_for_model_panel = []
        fields_in_types = []
        model_object = models[self.set_model]["object"]
        for x, y in model_object.types.items():
            types_for_model_panel.append(x)
            tempr_list = []
            for b in y.mandatory_atts:
                if b.name != "id" and b.name != "type":
                    tempr = b.label + " (" + translations["DefaultModelMandatoryText"][self.language] + ")"
                    tempr_list.append(tempr)

            for b in y.optional_atts:
                tempr = b.label
                tempr_list.append(tempr)
            fields_in_types.append(tempr_list)
        # print(types_for_model_panel)
        # print(fields_in_types)

        ij = 0
        strings_to_display = []
        for x in types_for_model_panel:
            string_to_display = ""
            fields_to_display = "<br>".join(fields_in_types[ij])
            string_to_display = "<u><b>" + x + "</b></u><br>" + fields_to_display
            strings_to_display.append(string_to_display)
            ij += 1

        strings_to_display = "<br>".join(strings_to_display)
        # print(strings_to_display)

        self.default_model_label.setText("<p><h3>" + translations["DefaultModelInfo"][self.language] + "</h3><h1>" + self.set_model + "</h1>" + strings_to_display + "</p>")

        self.RefreshDefaultModelMenu()
        self.RefreshModelMenus()

    def RefreshModelMenus(self):
        self.col_menu_new_col.clear()
        for x,y in models.items():
            if x == self.set_model:
                action = self.col_menu_new_col.addAction(x + " "+ translations["MainMenuChooseDefaultModelIsDefault"][self.language])
                action.setShortcut("Ctrl+N")
                action.triggered.connect(partial(self.NewCollection,model=x))
        for x,y in models.items():
            if x != self.set_model:
                action = self.col_menu_new_col.addAction(x)
                action.triggered.connect(partial(self.NewCollection, model=x))

        self.models_menu_default.clear()
        for x,y in models.items():
            if x != self.set_model:
                action = self.models_menu_default.addAction(x)
                action.triggered.connect(partial(self.setDefaultModel,model=x))
            else:
                action = self.models_menu_default.addAction(x + " "+ translations["MainMenuChooseDefaultModelIsDefault"][self.language])

        self.models_menu_copy_model.clear()
        for x,y in models.items():
            action = QAction(x,self)
            self.models_menu_copy_model.addAction(action)
            action.triggered.connect(partial(self.NewModelOpenWindow,model=x))

    def RefreshEditStyleMenu(self):
        try:
            self.styles_menu_edit_style.clear()
            for cmodel in models:
                newmenu = QMenu(cmodel, self)
                self.styles_menu_edit_style.addMenu(newmenu)
                for cit in self.CitationStylesList:
                    if cit.model.name == cmodel:
                        newaction = QAction(cit.name, self)
                        newaction.triggered.connect(partial(self.NewStyleWindow, edit=True, cit=cit))
                        newmenu.addAction(newaction)
        except Exception as e:
            print(e)

    def NewModelOpenWindow(self, checked=None, model=None):
        if checked == None: return

        dialog = QDialog()
        dialog.setStyleSheet('font-size: ' + str(self.fontsize) + 'pt;')
        self.NewModelWindowLayout = QGridLayout()
        dialog.setLayout(self.NewModelWindowLayout)
        dialog.setWindowTitle(translations["NewModelWindowTitle"][self.language])
        dialog.setStyleSheet(self.stylesheet_to_use)

        self.NewModelWindowMenu = QMenuBar()
        self.field_add_more = self.NewModelWindowMenu.addAction(translations["NewModelWindowAddField"][self.language], self.addField)
        self.types_add_more = self.NewModelWindowMenu.addAction(translations["NewModelWindowAddType"][self.language], self.addPubType)
        self.finalize_model = self.NewModelWindowMenu.addAction(translations["NewModelWindowFinalizeModel"][self.language], self.finalizeModel)
        self.NewModelWindowMenu.setStyleSheet("")
        self.NewModelWindowLayout.setMenuBar(self.NewModelWindowMenu)



        self.fieldWindowPosition = 2
        self.typeWindowPosition = 2
        self.fieldGUIcontroller = {}
        self.typeGUIcontroller = {}

        # self.field_add_more = QPushButton(translations["NewModelWindowAddField"][self.language])
        # self.field_add_more.clicked.connect(self.addField)
        # self.NewModelWindowLayout.addWidget(self.field_add_more, 1, 0)

        self.model_name = QLineEdit()
        self.model_name.setPlaceholderText(translations["NewModelWindowModelName"][self.language])
        self.NewModelWindowLayout.addWidget(self.model_name, 0, 0, 1, 10)

        self.IsManyLabel = QLabel(translations["NewModelWindowIsManyLabel"][self.language])
        self.FieldTypeLabel = QLabel(translations["NewModelWindowTypeLabel"][self.language])
        self.NewModelWindowLayout.addWidget(self.IsManyLabel, 1, 2)
        self.NewModelWindowLayout.addWidget(self.FieldTypeLabel, 1, 3)
        self.SeperationLabel = QLabel(translations["NewModelWindowSeperatedByCommas"][self.language])
        self.NewModelWindowLayout.addWidget(self.SeperationLabel, 1, 7, 1, 2)
        self.FieldNameLabel = QLabel(translations["NewModelWindowFieldNamePlaceholder"][self.language])
        self.FieldLabelLabel = QLabel(translations["NewModelWindowFieldLabelPlaceholder"][self.language])
        self.NewModelWindowLayout.addWidget(self.FieldNameLabel, 1, 0)
        self.NewModelWindowLayout.addWidget(self.FieldLabelLabel, 1, 1)
        self.TypeNameLabel = QLabel(translations["NewModelTypeName"][self.language])
        self.TypeLabelLabel = QLabel(translations["NewModelTypeLabel"][self.language])
        self.NewModelWindowLayout.addWidget(self.TypeNameLabel, 1, 5)
        self.NewModelWindowLayout.addWidget(self.TypeLabelLabel, 1, 6)

        self.addField(disabled=True)
        self.addField(disabled=True)
        self.addField()
        self.addPubType()

        if model is not None:
            model_object = models[model]["object"]
            fields_object_list = model_object.fields
            self.model_name.setText(model_object.name)
            type_counter = 2
            field_counter = 2
            len_counter = 0
            field_len_counter = 0
            #print(model_object.types)

            for x,y in model_object.types.items():
                len_counter += 1

            for x in fields_object_list:
                field_len_counter += 1

            i = 0
            while i < len_counter-1:
                self.addPubType()
                i += 1

            j = 0
            while j < field_len_counter-3:
                self.addField()
                j += 1


            for x,y in model_object.types.items():
                name = y.name
                label = y.label
                mands = y.mandatory_atts
                opts = y.optional_atts
                mand_list = []
                opt_list = []
                for man in mands:
                    mand_list.append(man.name)
                if "id" in mand_list:
                    mand_list.remove("id")
                if "type" in mand_list:
                    mand_list.remove("type")
                for op in opts:
                    opt_list.append(op.name)
                mand_ready_string = ",".join(mand_list)
                opt_ready_string = ",".join(opt_list)
                # print(mand_ready_string)
                # print(opt_ready_string)
                self.defineType(type_counter, name, label, mand_ready_string, opt_ready_string)
                type_counter += 1

            for x in fields_object_list:
                name = x.name
                label = x.label
                if x.is_many is True:
                    is_many_drop = 1
                else:
                    is_many_drop = 0
                if x._transform is str:
                    transform_drop = 0
                elif x._transform is int:
                    transform_drop = 1
                self.defineField(field_counter, name, label, is_many_drop, transform_drop)
                field_counter += 1

        else:
            self.defineField(2, "id", "", 0, 1)
            self.defineField(3, "type", "", 0, 0)

        #self.defineType(1, "B", "Knjiga", "TI", "AU")

        toto = QFrame()
        toto.setFrameShape(QFrame.VLine)
        toto.setFrameShadow(QFrame.Sunken)

        self.NewModelWindowLayout.addWidget(toto, 1, 4, 4, 1)

        # self.types_add_more = QPushButton(translations["NewModelWindowAddType"][self.language])
        # self.types_add_more.clicked.connect(self.addPubType)
        # self.NewModelWindowLayout.addWidget(self.types_add_more, 1, 5)

        dialog.exec_()

    def defineField(self, pos, name, label, ismany, type):
        for x,y in self.fieldGUIcontroller.items():
            if x is pos:
                y["name"].setText(name)
                y["label"].setText(label)
                y["ismany"].setCurrentIndex(ismany)
                y["type"].setCurrentIndex(type)

    def addField(self, disabled=False):
        self.field_name = QLineEdit()
        self.field_name.setPlaceholderText(translations["NewModelWindowFieldNamePlaceholder"][self.language])
        self.field_label = QLineEdit()
        self.field_label.setPlaceholderText(translations["NewModelWindowFieldLabelPlaceholder"][self.language])
        self.field_ismany = QComboBox()
        self.field_ismany.addItem(translations["False"][self.language])
        self.field_ismany.addItem(translations["True"][self.language])
        self.field_type = QComboBox()
        self.field_type.addItem(translations["NewModelWindowFieldTypeString"][self.language])
        self.field_type.addItem(translations["NewModelWindowFieldTypeInteger"][self.language])

        if disabled is True:
            self.field_name.setDisabled(True)
            self.field_ismany.setDisabled(True)
            self.field_type.setDisabled(True)

        # if self.fieldWindowPosition is 1:
        #     self.field_name.setText("id")
        #     self.field_ismany.setCurrentIndex(0)
        #     self.field_type.setCurrentIndex(1)
        # elif self.fieldWindowPosition is 2:
        #     self.field_name.setText("type")
        #     self.field_ismany.setCurrentIndex(0)
        #     self.field_type.setCurrentIndex(0)

        self.NewModelWindowLayout.addWidget(self.field_name, self.fieldWindowPosition, 0)
        self.NewModelWindowLayout.addWidget(self.field_label, self.fieldWindowPosition, 1)
        self.NewModelWindowLayout.addWidget(self.field_ismany, self.fieldWindowPosition, 2)
        self.NewModelWindowLayout.addWidget(self.field_type, self.fieldWindowPosition, 3)

        self.fieldGUIcontroller[self.fieldWindowPosition] = {"name": self.field_name, "label": self.field_label, "ismany": self.field_ismany, "type": self.field_type}
        self.fieldWindowPosition += 1

    def defineType(self, pos, name, label, man, opt):
        for x,y in self.typeGUIcontroller.items():
            if x is pos:
                y["name"].setText(name)
                y["label"].setText(label)
                y["mand"].setText(man)
                y["opt"].setText(opt)

    def addPubType(self):
        self.type_name = QLineEdit()
        self.type_name.setPlaceholderText(translations["NewModelTypeName"][self.language])
        self.type_label = QLineEdit()
        self.type_label.setPlaceholderText(translations["NewModelTypeLabel"][self.language])
        self.mand_fields = QLineEdit()
        self.mand_fields.setPlaceholderText(translations["NewModelTypeMandatoryFields"][self.language])
        self.opt_fields = QLineEdit()
        self.opt_fields.setPlaceholderText(translations["NewModelTypeOptionalFields"][self.language])

        self.NewModelWindowLayout.addWidget(self.type_name, self.typeWindowPosition, 5)
        self.NewModelWindowLayout.addWidget(self.type_label, self.typeWindowPosition, 6)
        self.NewModelWindowLayout.addWidget(self.mand_fields, self.typeWindowPosition, 7)
        self.NewModelWindowLayout.addWidget(self.opt_fields, self.typeWindowPosition, 8)

        self.typeGUIcontroller[self.typeWindowPosition] = {"name": self.type_name, "label": self.type_label, "mand": self.mand_fields, "opt": self.opt_fields}
        self.typeWindowPosition += 1

    def finalizeModel(self):
        try:
            fields = []
            types = []
            for x, y in self.fieldGUIcontroller.items():
                ismany = y["ismany"].currentIndex()
                type = y["type"].currentIndex()

                if ismany is 0:
                    ismany = False
                elif ismany is 1:
                    ismany = True

                if type is 0:
                    type = str
                elif type is 1:
                    type = int

                new_field = ModelField(y["name"].text(),y["label"].text(),ismany,type)
                fields.append(new_field)

            for x, y in self.typeGUIcontroller.items():
                mand_list = y["mand"].text().split(",")
                opt_list = y["opt"].text().split(",")
                mand_object_list = []
                opt_object_list = []
                for f in fields:
                    if f.name in mand_list:
                        mand_object_list.append(f)
                    if f.name in opt_list:
                        opt_object_list.append(f)
                    if f.name == "id" or f.name == "type":
                        mand_object_list.append(f)

                new_type = ModelType(y["name"].text(),y["label"].text(),mand_object_list, opt_object_list)
                types.append(new_type)

            new_model = DataModel(self.model_name.text(), types)
            models[new_model.name] = {"name": new_model.name, "object": new_model}
            #print(models)
            SaveToJson(new_model)
            self.UpdateListOfModels()
            self.RefreshModelMenus()
            self.RefreshDefaultModelInfo()
            self.OKdialog(translations["ModelCreated"][self.language])
            self.NewModelWindowLayout.parent().close()

        except Exception as e:
            print(e)

    def UpdateListOfModels(self):
        import loaded_models
        list_of_models = []
        for x, y in models.items():
            list_of_models.append(x)
        list_of_models_for_display = "<br>".join(list_of_models)

        if list_of_models:
            self.all_models_label.setText(
                "<p><h3>" + translations["AllModelsPanelText"][self.language] + "</h3><h1>" + str(
                    len(list_of_models)) + "</h1>" + list_of_models_for_display + "</p>")

    def setDefaultModel(self, model=None):
        self.settings["default_model"] = model
        self.set_model = self.settings["default_model"]
        StoreSettings(self.settings)
        #self.OKdialog(translations["SettingDefaultRestartApp"][self.language])
        self.RefreshDefaultModelInfo()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def OKdialog(self, info):
        dialog = QDialog()
        dialog.setStyleSheet(self.stylesheet_to_use)
        self.OKDialogLayout = QGridLayout()
        dialog.setLayout(self.OKDialogLayout)
        dialog.setWindowTitle(translations["OKDialogTitle"][self.language])

        info_label = QLabel(info)
        self.OKDialogLayout.addWidget(info_label, 0, 0)
        ok_button = QPushButton(translations["OKButtonUniversal"][self.language])
        ok_button.clicked.connect(dialog.close)
        self.OKDialogLayout.addWidget(ok_button, 1, 0)


        dialog.exec_()

    def NewCollection(self, model):
        try:
            self.model_in_use = models[model]["object"]
            self.col = Collection(self.model_in_use)

            sender = self.sender()
            grid = QGridLayout()
            grid.setSpacing(10)
            self.setLayout(grid)

            mainwidget = QWidget()
            self.setCentralWidget(mainwidget)
            mainwidget.setLayout(grid)

            self.collection_frame = QFrame()
            self.collection_frame.setFrameStyle(QFrame.StyledPanel)
            grid.addWidget(self.collection_frame, 0, 0, 7, 9)

            # Container Widget
            self.collection_view_widget = QWidget()
            #self.collection_view_widget.setStyleSheet("border:1px solid black;")
            # Layout of Container Widget
            self.collection_layout = QGridLayout(self)
            self.collection_layout.setAlignment(QtCore.Qt.AlignTop)
            self.collection_view_widget.setLayout(self.collection_layout)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            #scroll.setMaximumHeight(500)
            #scroll.setMaximumWidth(500)
            scroll.setFrameStyle(QFrame.StyledPanel)

            scroll.setWidget(self.collection_view_widget)

            grid.addWidget(scroll, 0, 0, 7, 9)


            #grid.addWidget(self.collection_view_widget, 0, 0, 7, 9)

            # self.collection_view = QTreeWidget()
            # self.collection_view.setFrameStyle(QFrame.StyledPanel)
            # self.collection_view.setFrameShadow(QFrame.Sunken)
            # grid.addWidget(self.collection_view, 0, 0, 7, 9)

            self.details_view = QFrame()
            self.details_view.setFrameStyle(QFrame.StyledPanel)
            grid.addWidget(self.details_view, 0, 10, 7, 9)

            self.detalis_view_widget = QWidget()
            # self.collection_view_widget.setStyleSheet("border:1px solid black;")
            # Layout of Container Widget
            self.details_layout = QGridLayout(self)
            self.details_layout.setAlignment(QtCore.Qt.AlignTop)
            self.detalis_view_widget.setLayout(self.details_layout)

            details_scroll = QScrollArea()
            details_scroll.setWidgetResizable(True)
            # scroll.setMaximumHeight(500)
            # scroll.setMaximumWidth(500)
            details_scroll.setFrameStyle(QFrame.StyledPanel)

            details_scroll.setWidget(self.detalis_view_widget)

            grid.addWidget(details_scroll, 0, 10, 7, 9)

            if self.settings["button_style"] == "Icon only":
                self.group_btn = QPushButton("")
                self.filter_btn = QPushButton("")
                self.prepare_items_btn = QPushButton("")
                self.import_btn = QPushButton("")
                self.additem_btn = QPushButton("")
                self.validate_col = QPushButton("")
                self.load_col_state = QPushButton("")
                self.edit_col_view = QPushButton("")
                self.garbage_btn = QPushButton("")
                self.group_btn.setIcon(QtGui.QIcon("icons/layers.png"))
                self.filter_btn.setIcon(QtGui.QIcon("icons/focus.png"))
                self.prepare_items_btn.setIcon(QtGui.QIcon("icons/notepad-2.png"))
                self.import_btn.setIcon(QtGui.QIcon("icons/add-3.png"))
                self.additem_btn.setIcon(QtGui.QIcon("icons/plus.png"))
                self.validate_col.setIcon(QtGui.QIcon("icons/check_mark.png"))
                self.load_col_state.setIcon(QtGui.QIcon("icons/tabs-1.png"))
                self.edit_col_view.setIcon(QtGui.QIcon("icons/settings-4.png"))
                self.garbage_btn.setIcon(QtGui.QIcon("icons/garbage-1.png"))
            elif self.settings["button_style"] == "Icon and text":
                self.group_btn = QPushButton(translations["GroupButton"][self.language])
                self.filter_btn = QPushButton(translations["FilterButton"][self.language])
                self.prepare_items_btn = QPushButton(translations["PrepareItemsButton"][self.language])
                self.import_btn = QPushButton(translations["ImportFromFilesButton"][self.language])
                self.additem_btn = QPushButton(translations["AddItemButton"][self.language])
                self.validate_col = QPushButton(translations["ValidateCollection"][self.language])
                self.load_col_state = QPushButton(translations["LoadCollectionState"][self.language])
                self.edit_col_view = QPushButton(translations["EditCollectionView"][self.language])
                self.garbage_btn = QPushButton(translations["TrashBin"][self.language])
                self.group_btn.setIcon(QtGui.QIcon("icons/layers.png"))
                self.filter_btn.setIcon(QtGui.QIcon("icons/focus.png"))
                self.prepare_items_btn.setIcon(QtGui.QIcon("icons/notepad-2.png"))
                self.import_btn.setIcon(QtGui.QIcon("icons/add-3.png"))
                self.additem_btn.setIcon(QtGui.QIcon("icons/plus.png"))
                self.validate_col.setIcon(QtGui.QIcon("icons/folder-7.png"))
                self.load_col_state.setIcon(QtGui.QIcon("icons/tabs-1.png"))
                self.edit_col_view.setIcon(QtGui.QIcon("icons/settings-4.png"))
                self.garbage_btn.setIcon(QtGui.QIcon("icons/garbage-1.png"))

            btn_style = "padding:5px;"

            self.group_btn.setStyleSheet(btn_style)
            self.filter_btn.setStyleSheet(btn_style)
            self.prepare_items_btn.setStyleSheet(btn_style)
            self.import_btn.setStyleSheet(btn_style)
            self.additem_btn.setStyleSheet(btn_style)
            self.validate_col.setStyleSheet(btn_style)
            self.load_col_state.setStyleSheet(btn_style)
            self.edit_col_view.setStyleSheet(btn_style)
            self.garbage_btn.setStyleSheet(btn_style)

            self.group_btn.setStatusTip(translations["GroupButton"][self.language])
            self.filter_btn.setStatusTip(translations["FilterButton"][self.language])
            self.prepare_items_btn.setStatusTip(translations["PrepareItemsButton"][self.language])
            self.import_btn.setStatusTip(translations["ImportFromFilesButton"][self.language])
            self.additem_btn.setStatusTip(translations["AddItemButton"][self.language])
            self.validate_col.setStatusTip(translations["ValidateCollection"][self.language])
            self.load_col_state.setStatusTip(translations["LoadCollectionState"][self.language])
            self.edit_col_view.setStatusTip(translations["EditCollectionView"][self.language])
            self.garbage_btn.setStatusTip(translations["TrashBin"][self.language])

            grid.addWidget(self.group_btn, 8, 0, 1, 1)
            grid.addWidget(self.filter_btn, 8, 1, 1, 1)
            grid.addWidget(self.prepare_items_btn, 8, 2, 1, 1)
            grid.addWidget(self.edit_col_view, 8, 3, 1, 1)
            grid.addWidget(self.garbage_btn, 8, 4, 1, 1)
            grid.addWidget(self.import_btn, 8, 5, 1, 1)
            grid.addWidget(self.additem_btn, 8, 6, 1, 1)
            grid.addWidget(self.validate_col, 8, 7, 1, 1)
            grid.addWidget(self.load_col_state, 8, 8, 1, 1)

            self.delete_selected_button = QPushButton(translations["RemoveSelectedItemsButton"][self.language])
            self.delete_selected_button.setStyleSheet("background-color:"+self.warning_color+";color:"+self.highlighted_text_color+";")
            self.delete_selected_button.clicked.connect(partial(self.ConfirmDelete, self.col._selected_items, selected=True))
            grid.addWidget(self.delete_selected_button, 8, 10, 1, 9)
            self.delete_selected_button.hide()

            self.additem_btn.setShortcut("+")
            self.group_btn.setShortcut("Ctrl+G")
            self.edit_col_view.setShortcut("Ctrl+V")
            self.garbage_btn.setShortcut("F4")
            self.filter_btn.setShortcut("Ctrl+F")
            self.prepare_items_btn.setShortcut("Shift+P")
            self.import_btn.setShortcut("Ctrl+I")

            self.additem_btn.clicked.connect(self.AddNewItemWindow)
            self.edit_col_view.clicked.connect(self.EditColViewWindow)
            self.group_btn.clicked.connect(self.GroupingWindow)
            self.garbage_btn.clicked.connect(self.RecycleBinWindow)
            self.import_btn.clicked.connect(self.UniversalImportWindow)
            self.filter_btn.clicked.connect(self.FilteringWindow)
            self.prepare_items_btn.clicked.connect(self.PrepareItemsWindow)
            self.validate_col.clicked.connect(self.ValidateCollection)

            self.ColStatesMenu = QMenu()
            self.ColUndo = QAction(translations["ColBack"][self.language], self)
            self.ColUndo.setShortcut("Ctrl+Z")
            self.ColUndo.triggered.connect(partial(self.HandleStates, undo=True))
            self.ColUndo.setDisabled(True)
            self.ColRedo = QAction(translations["ColRedo"][self.language], self)
            self.ColRedo.triggered.connect(partial(self.HandleStates, redo=True))
            self.ColRedo.setDisabled(True)
            self.ColRedo.setShortcut("Ctrl+Shift+Z")
            self.ColStatesMenu.addAction(self.ColUndo)
            self.ColStatesMenu.addAction(self.ColRedo)
            self.load_col_state.setMenu(self.ColStatesMenu)

            self.checked_items_dict = {}
            self.CurrentGroupingParams = []
            self.FiltersHandler = {}
            self.FiltersDict = {}
            self.FiltersCounter = 0
            self.TempLoadPosition = -1

            self.LoadCitationStyles()
            self.LoadAPA()

        except Exception as e:
            print(e)

    def FireTempSave(self):
        if self.TempLoadPosition != -1:
            self.col.TempSave(new=True, pos=self.TempLoadPosition+1)
            self.TempLoadPosition = -1
        else:
            self.col.TempSave()
        self.CheckUndoRedo()

    def CheckUndoRedo(self):
        length = len(self.col._saves)
        if self.TempLoadPosition == 0-length:
            self.ColUndo.setDisabled(True)
        else:
            self.ColUndo.setDisabled(False)
        if self.TempLoadPosition == -1:
            self.ColRedo.setDisabled(True)
        else:
            self.ColRedo.setDisabled(False)

    def HandleStates(self, undo=False, redo=False):
        try:
            if undo:
                self.TempLoadPosition -= 1
                self.col.TempLoad(self.TempLoadPosition)
            elif redo:
                self.TempLoadPosition += 1
                self.col.TempLoad(self.TempLoadPosition)
            self.RefreshCollectionView()
            self.CheckUndoRedo()
        except Exception as e:
            self.OKdialog(str(e))

    def ValidateCollection(self):
        self.FireTempSave()
        self.import_reporter_handler = []
        if self.col._data:
            for key, item in self.col._data.items():
                empty, invalid, faultyitem = self.col.validateItem(item)
                if empty or invalid or faultyitem:
                    self.import_reporter_handler.append([empty, invalid, faultyitem])
        self.RefreshCollectionView()
        if self.import_reporter_handler:
            self.ImportErrorReportWindow()
        else:
            self.OKdialog(translations["CollectionValid"][self.language])
        self.FireTempSave()

    def UniversalImportWindow(self):
        self.files_to_import_list = []

        self.supported_formats = {"BibTeX": "bib", "CSV": "csv", "MARC": "mrc"}

        dialog = QDialog()
        dialog.setStyleSheet('font-size: ' + str(self.fontsize) + 'pt;')
        dialog.setStyleSheet(self.stylesheet_to_use)
        self.UniversalImportWindowLayout = QGridLayout()
        dialog.setLayout(self.UniversalImportWindowLayout)
        dialog.setWindowTitle(translations["UniversalImportWindowTitle"][self.language])

        self.import_scroll_widget = QWidget()
        self.import_scroll_layout = QGridLayout(self)
        self.import_scroll_layout.setAlignment(QtCore.Qt.AlignTop)
        self.import_scroll_widget.setLayout(self.import_scroll_layout)
        import_scroll = QScrollArea()
        import_scroll.setWidgetResizable(True)
        import_scroll.setMinimumHeight(400)
        import_scroll.setFrameStyle(QFrame.StyledPanel)
        import_scroll.setWidget(self.import_scroll_widget)
        self.UniversalImportWindowLayout.addWidget(import_scroll, 1, 0, 1, 3)


        self.ChooseFilesForImportButton = QPushButton(translations["ChooseFilesForImport"][self.language])
        self.ChooseFilesForImportButton.clicked.connect(self.AddFilesForImport)
        self.UniversalImportWindowLayout.addWidget(self.ChooseFilesForImportButton, 2, 0)

        self.ValidateOnImportCheckBox = QCheckBox(translations["ValidateOnImport"][self.language])
        self.UniversalImportWindowLayout.addWidget(self.ValidateOnImportCheckBox, 2, 1)

        self.TryTransformOnImportCheckBox = QCheckBox(translations["TransformOnImport"][self.language])
        self.UniversalImportWindowLayout.addWidget(self.TryTransformOnImportCheckBox, 2, 2)

        toto1 = QFrame()
        toto1.setFrameShape(QFrame.HLine)
        toto1.setFrameShadow(QFrame.Sunken)

        self.UniversalImportWindowLayout.addWidget(toto1, 3, 0, 1, 3)

        self.ExecuteImportFilesButton = QPushButton(translations["ImportFilesButton"][self.language])
        self.ExecuteImportFilesButton.clicked.connect(self.ExecuteImportHandler)
        self.UniversalImportWindowLayout.addWidget(self.ExecuteImportFilesButton, 4, 0, 1, 3)

        dialog.exec_()

    def AddFilesForImport(self):
        open_file = QFileDialog()
        open_file.setFileMode(QFileDialog.ExistingFiles)
        files_to_open = open_file.getOpenFileNames(self)

        for file in files_to_open[0]:
            if file not in self.files_to_import_list:
                self.files_to_import_list.append(file)

        self.GenerateFilesHandler()

    def GenerateFilesHandler(self):
        for i in reversed(range(self.import_scroll_layout.count())):
            self.import_scroll_layout.itemAt(i).widget().setParent(None)

        self.import_handler = {}

        for file in self.files_to_import_list:
            full_file_path = file
            short_file_name = file.split("/")[-1]

            file_label = QLabel(short_file_name)
            self.import_scroll_layout.addWidget(file_label, self.files_to_import_list.index(file), 1)

            formats_combo = QComboBox()
            formats_combo.currentIndexChanged.connect(self.ChangeCSVMapperVisibility)
            for format in self.supported_formats.keys():
                formats_combo.addItem(format)
            self.import_scroll_layout.addWidget(formats_combo, self.files_to_import_list.index(file), 2)


            csv_mappers_combo = QComboBox()
            with open("models/"+self.model_in_use.name+"/mappers/csv.json") as json_data:
                csv_dict = json.load(json_data)
            for x in csv_dict.keys():
                csv_mappers_combo.addItem(x)
            self.import_scroll_layout.addWidget(csv_mappers_combo, self.files_to_import_list.index(file), 3)

            extension = short_file_name.split(".")[-1]
            info_label = QLabel(extension)
            info_label.setAlignment(QtCore.Qt.AlignCenter)
            info_label.setMaximumWidth(50)
            if extension in self.supported_formats.values():
                info_label.setStyleSheet("background-color:#A7E8B8;")
            else:
                info_label.setStyleSheet("background-color:#E8A7A7;")
            self.import_scroll_layout.addWidget(info_label, self.files_to_import_list.index(file), 0)

            for x, y in self.supported_formats.items():
                if extension == y:
                    index = formats_combo.findText(x, QtCore.Qt.MatchFixedString)
                    if index >= 0:
                        formats_combo.setCurrentIndex(index)

            self.import_handler[self.files_to_import_list.index(file)] = {"file": full_file_path, "format_combo": formats_combo, "mappers": csv_mappers_combo}

            self.ChangeCSVMapperVisibility()

    def ChangeCSVMapperVisibility(self):
        for y in self.import_handler.values():
            if y["format_combo"].currentText() != "CSV":
                y["mappers"].hide()
            else:
                y["mappers"].show()

    def ExecuteImportHandler(self):
        self.FireTempSave()
        self.import_reporter_handler = []
        try:
            if self.ValidateOnImportCheckBox.isChecked():
                to_validate = True
            else:
                to_validate = False
            if self.TryTransformOnImportCheckBox.isChecked():
                to_transform = True
            else:
                to_transform = False

            for y in self.import_handler.values():
                if y["format_combo"].currentText() == "CSV":
                    ## IMPORT CSV
                    items = formats.CSV.mapper_function.MapCSV(y["file"], self.model_in_use, y["mappers"].currentText())
                    for item in items:
                        if to_validate is True:
                            empty, invalid, faultyitem = self.col.addItem(**item, _validate=to_validate, _transform=to_transform)
                            if empty or invalid:
                                self.import_reporter_handler.append([empty,invalid,faultyitem])
                        else:
                            self.col.addItem(**item, _validate=to_validate, _transform=to_transform)
                elif y["format_combo"].currentText() == "MARC":
                    items = formats.MARC.mapper_function.MapUNIMARC(y["file"],self.model_in_use)
                    print(items)
                    for item in items:
                        if to_validate is True:
                            empty, invalid, faultyitem = self.col.addItem(**item, _validate=to_validate, _transform=to_transform)
                            if empty or invalid:
                                self.import_reporter_handler.append([empty,invalid,faultyitem])
                        else:
                            self.col.addItem(**item, _validate=to_validate, _transform=to_transform)
                elif y["format_combo"].currentText() == "BibTeX":
                    #print("IMPORT BIBTEX")
                    items = formats.BibTeX.mapper_function.MapBIBTEX(y["file"], self.model_in_use)
                    print(items)
                    for item in items:
                        if to_validate is True:
                            empty, invalid, faultyitem = self.col.addItem(**item, _validate=to_validate, _transform=to_transform)
                            if empty or invalid:
                                self.import_reporter_handler.append([empty,invalid,faultyitem])
                        else:
                            self.col.addItem(**item, _validate=to_validate, _transform=to_transform)
        except Exception as e:
            print(e)
        #print(self.import_reporter_handler)
        self.RefreshCollectionView()
        if self.import_reporter_handler:
            self.ImportErrorReportWindow()
        self.FireTempSave()
        self.UniversalImportWindowLayout.parent().close()

    def ImportErrorReportWindow(self):
        try:
            dialog = QDialog()
            dialog.setStyleSheet('font-size: ' + str(self.fontsize) + 'pt;')
            dialog.setStyleSheet(self.stylesheet_to_use)
            self.ImportErrorReportLayout = QGridLayout()
            dialog.setLayout(self.ImportErrorReportLayout)
            dialog.setWindowTitle(translations["ImportErrorReportWindowTitle"][self.language])

            summary_label = QLabel("<h3>"+translations["ImportErrorReportSummaryTitle"][self.language]+"</h3>")
            self.ImportErrorReportLayout.addWidget(summary_label, 0, 0, 1, 3)

            total_invalid = len(self.import_reporter_handler)
            total_label = QLabel("<b>{}</b>: {}".format(translations["TotalNumberOfInvalidItems"][self.language], str(total_invalid)))
            self.ImportErrorReportLayout.addWidget(total_label, 1, 0, 1, 3)

            total_missing = self.CountForInvalid(0)
            total_faulty = self.CountForInvalid(1)

            total_missing_label = QLabel("<b>{}</b>: {}".format(translations["TotalMissingLabel"][self.language], str(total_missing)))
            self.ImportErrorReportLayout.addWidget(total_missing_label, 2, 0, 1, 3)

            total_faulty_label = QLabel("<b>{}</b>: {}".format(translations["TotalFaultyLabel"][self.language], str(total_faulty)))
            self.ImportErrorReportLayout.addWidget(total_faulty_label, 3, 0, 1, 3)

            self.report_scroll_widget = QWidget()
            self.report_scroll_layout = QGridLayout(self)
            self.report_scroll_layout.setAlignment(QtCore.Qt.AlignTop)
            self.report_scroll_widget.setLayout(self.report_scroll_layout)
            report_scroll = QScrollArea()
            report_scroll.setWidgetResizable(True)
            report_scroll.setMinimumHeight(400)
            report_scroll.setMinimumWidth(400)
            report_scroll.setFrameStyle(QFrame.StyledPanel)
            report_scroll.setWidget(self.report_scroll_widget)
            self.ImportErrorReportLayout.addWidget(report_scroll, 4, 0, 1, 3)

            self.invalid_ids = []

            self.fix_all_errors_button = QPushButton(translations["ErrorReportFixAll"][self.language])
            self.include_all_errors_button = QPushButton(translations["ErrorReportIncludeAll"][self.language])
            self.include_all_errors_button.clicked.connect(partial(self.FireIncludeAll, window=dialog))
            self.exclude_all_errors_button = QPushButton(translations["ErrorReportExcludeAll"][self.language])

            self.ImportErrorReportLayout.addWidget(self.fix_all_errors_button, 5, 0)
            self.ImportErrorReportLayout.addWidget(self.include_all_errors_button, 5, 1)
            self.ImportErrorReportLayout.addWidget(self.exclude_all_errors_button, 5, 2)

            self.FillErrorReportScroll()

            self.exclude_all_errors_button.clicked.connect(partial(self.FireExcludeAll, self.invalid_ids, dialog))
            self.fix_all_errors_button.clicked.connect(partial(self.FireFixAll, self.invalid_ids, dialog))
        except Exception as e:
            print(e)

        #print(self.import_reporter_handler)

        dialog.exec_()

    def FillErrorReportScroll(self):
        intern_counter = 0
        print(self.import_reporter_handler)

        missings = 0
        faultys = 1
        item_itself = 2
        for list in self.import_reporter_handler:

            item_block_handler = []

            invalid_item_id = list[item_itself]["id"]
            self.invalid_ids.append(invalid_item_id)

            list_of_missings = []
            string_of_missings = ""
            if list[missings]:
                for miss in list[missings]:
                    list_of_missings.append(miss.label)
                string_of_missings = ", ".join(list_of_missings)

            list_of_faultys = []
            string_of_faultys = ""
            if list[faultys]:
                for faulty in list[faultys]:
                    list_of_faultys.append("{}: {}".format(faulty.label, list[item_itself][faulty.name]))
            string_of_faultys = "<br>".join(list_of_faultys)

            item_info_title_label = QLabel("<h4>{} ID#{}</h4>".format(translations["InvalidItemLabel"][self.language], str(invalid_item_id)))
            item_info_title_label.setStyleSheet("color:"+self.accent_color+";padding:5px 5px 0 5px;")
            self.report_scroll_layout.addWidget(item_info_title_label, intern_counter, 0, 1, 4)
            item_block_handler.append(item_info_title_label)
            intern_counter+=1

            if string_of_missings:
                item_missings_label = QLabel("<b>{}</b><br>{}".format(translations["MissingFieldsLabel"][self.language], string_of_missings))
                item_missings_label.setStyleSheet("padding:5px;")
                self.report_scroll_layout.addWidget(item_missings_label, intern_counter, 0, 1, 4)
                item_block_handler.append(item_missings_label)
                intern_counter+=1

            if string_of_faultys:
                item_faultys_label = QLabel("<b>{}</b><br>{}".format(translations["FaultyValuesLabel"][self.language], string_of_faultys))
                item_faultys_label.setStyleSheet("padding:5px;")
                self.report_scroll_layout.addWidget(item_faultys_label, intern_counter, 0, 1, 4)
                item_block_handler.append(item_faultys_label)
                intern_counter+=1

            self.col._data[invalid_item_id] = list[item_itself]
            fix_item_button = QPushButton(translations["ErrorReportFixItemButton"][self.language])
            exclude_item_button = QPushButton(translations["ErrorReportExcludeItemButton"][self.language])
            include_item_button = QPushButton(translations["ErrorReportIncludeItemButton"][self.language])
            context_button = QPushButton(translations["ErrorReportContextItemButton"][self.language])

            fix_item_button.setStyleSheet("margin:0 0 5px 5px;")
            context_button.setStyleSheet("margin:0 0 5px 0;")
            exclude_item_button.setStyleSheet("margin:0 0 5px 0;")
            include_item_button.setStyleSheet("margin:0 5px 5px 0;")

            self.report_scroll_layout.addWidget(fix_item_button, intern_counter, 0)
            item_block_handler.append(fix_item_button)
            self.report_scroll_layout.addWidget(context_button, intern_counter, 1)
            item_block_handler.append(context_button)
            self.report_scroll_layout.addWidget(exclude_item_button, intern_counter, 2)
            item_block_handler.append(exclude_item_button)
            self.report_scroll_layout.addWidget(include_item_button, intern_counter, 3)
            item_block_handler.append(include_item_button)

            intern_counter+=1

            toto1 = QFrame()
            toto1.setFrameShape(QFrame.HLine)
            toto1.setFrameShadow(QFrame.Sunken)

            self.report_scroll_layout.addWidget(toto1, intern_counter, 0, 1, 4)
            item_block_handler.append(toto1)

            fix_item_button.clicked.connect(partial(self.FireFixItem, editer=list[item_itself]["id"], itemblock=item_block_handler))
            exclude_item_button.clicked.connect(partial(self.FireExcludeItem, itemid=[invalid_item_id], itemblock=item_block_handler))
            context_button.clicked.connect(partial(self.ContextWindow, list[item_itself]))
            include_item_button.clicked.connect(partial(self.FireIncludeItem, itemblock=item_block_handler))

            intern_counter+=1

    def FireFixAll(self, itemsid, window):
        self.FireTempSave()
        window.close()
        for id in itemsid:
            self.AddNewItemWindow(edit=id)
            self.RefreshCollectionView()
        self.FireTempSave()

    def FireIncludeAll(self, window):
        self.FireTempSave()
        window.close()
        self.RefreshCollectionView()
        self.FireTempSave()

    def FireExcludeAll(self, itemsid, window):
        try:
            self.FireTempSave()
            self.col.removeItems(itemsid)
            self.RefreshCollectionView()
            window.close()
            self.FireTempSave()
        except Exception as e:
            print(e)

    def FireIncludeItem(self, itemblock):
        self.FireTempSave()
        for each in itemblock:
            each.setParent(None)
        self.RefreshCollectionView()
        self.FireTempSave()

    def FireExcludeItem(self, itemid, itemblock):
        try:
            self.FireTempSave()
            self.col.removeItems(itemid)
            for each in itemblock:
                each.setParent(None)
            self.RefreshCollectionView()
            self.FireTempSave()
        except Exception as e:
            print(e)

    def FireFixItem(self, editer, itemblock):
        try:
            self.FireTempSave()
            self.AddNewItemWindow(edit=editer)
            for each in itemblock:
                each.setParent(None)
            self.RefreshCollectionView()
            self.FireTempSave()
        except Exception as e:
            print(e)

    def ContextWindow(self, item):
        dialog = QDialog()
        dialog.setStyleSheet('font-size: ' + str(self.fontsize) + 'pt;')
        dialog.setStyleSheet(self.stylesheet_to_use)
        self.ContextLayout = QGridLayout()
        dialog.setLayout(self.ContextLayout)
        dialog.setWindowTitle(translations["ContextWindowTitle"][self.language])

        self.ContextScrollWidget = QWidget()
        self.ContextScrollLayout = QGridLayout(self)
        self.ContextScrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.ContextScrollWidget.setLayout(self.ContextScrollLayout)

        rec_scroll = QScrollArea()
        rec_scroll.setMinimumHeight(500)
        rec_scroll.setMinimumWidth(500)
        rec_scroll.setWidgetResizable(True)
        rec_scroll.setFrameStyle(QFrame.StyledPanel)

        rec_scroll.setWidget(self.ContextScrollWidget)

        self.ContextLayout.addWidget(rec_scroll, 0, 0)

        pos_counter = 0
        for x, y in item.items():
            for field in self.col.model.fields:
                if field.name == x:
                    labelo = QLabel(field.label)
                    labelo.setStyleSheet("color:{};text-transform: uppercase;".format(self.accent_color))
                    self.ContextScrollLayout.addWidget(labelo, pos_counter, 0, 1, 2)
                    pos_counter+=1
                    if type(y) is list:
                        y = list(filter(None, y)) # fastest
                        if y:
                            values = []
                            for each in y:
                                values.append(each)
                            for value in values:
                                type_label = QLabel(str(type(value).__name__))
                                type_label.setMinimumWidth(30)
                                type_label.setMaximumWidth(40)
                                type_label.setAlignment(QtCore.Qt.AlignCenter)
                                if type(value) == field._transform:
                                    type_label.setStyleSheet(
                                        "text-transform: uppercase; color:{}; background-color:{};".format(
                                            self.highlighted_text_color, self.accent_color))
                                else:
                                    type_label.setStyleSheet(
                                        "text-transform: uppercase; color:{}; background-color:{};".format(
                                            self.highlighted_text_color, self.warning_color))
                                self.ContextScrollLayout.addWidget(type_label, pos_counter, 0)
                                each_value_label = QLabel(value)
                                self.ContextScrollLayout.addWidget(each_value_label, pos_counter, 1)
                                pos_counter += 1
                        else:
                            nodata = QLabel(translations["ContextNoData"][self.language])
                            nodata.setStyleSheet("color:{};".format(self.warning_color))
                            self.ContextScrollLayout.addWidget(nodata, pos_counter, 0, 1, 2)
                            pos_counter += 1
                    else:
                        if y:
                            type_label = QLabel(str(type(y).__name__))
                            type_label.setMinimumWidth(30)
                            type_label.setMaximumWidth(40)
                            type_label.setAlignment(QtCore.Qt.AlignCenter)
                            if type(y) == field._transform:
                                type_label.setStyleSheet("text-transform: uppercase; color:{}; background-color:{};".format(self.highlighted_text_color, self.accent_color))
                            else:
                                type_label.setStyleSheet("text-transform: uppercase; color:{}; background-color:{};".format(self.highlighted_text_color, self.warning_color))
                            self.ContextScrollLayout.addWidget(type_label, pos_counter, 0)
                            if x == "type":
                                for dtype in self.col.model.data_types:
                                    if dtype.name == y:
                                        value_label = QLabel(str(dtype.label))
                            else:
                                value_label = QLabel(str(y))
                            self.ContextScrollLayout.addWidget(value_label, pos_counter, 1)
                            pos_counter+=1
                        else:
                            nodata = QLabel(translations["ContextNoData"][self.language])
                            nodata.setStyleSheet("color:{};".format(self.warning_color))
                            self.ContextScrollLayout.addWidget(nodata, pos_counter, 0, 1, 2)
                            pos_counter += 1

        dialog.exec_()

    def CountForInvalid(self, position):
        total_no = 0
        for list in self.import_reporter_handler:
            if list[position]:
                for field in list[position]:
                    total_no+=1
        return total_no

    def TryImportCSV(self):
        self.FireTempSave()
        items = formats.CSV.mapper_function.MapCSV("input_files/savedrecs - Copy.txt", self.model_in_use, "Web of Science")
        for item in items:
            empty, invalid = self.col.addItem(**item, _validate=True, _transform=True)
        self.RefreshCollectionView()
        self.FireTempSave()

    def GenerateTypeDropDown(self):
        self.type_track_dict = []
        self.fields_inputs_dict = {}
        self.add_item_scrollable_panel.setAlignment(QtCore.Qt.AlignTop)
        for x,y in self.model_in_use.types.items():
            self.addItemTypeDropDown.addItem(y.label)
            self.type_track_dict.append(y)
        self.GenerateAddItemWidgets()
        for x, y in self.fields_inputs_dict.items():
            if x != "type":
                y.setStyleSheet("")

    def GenerateAddItemWidgets(self):
        try:
            for i in reversed(range(self.add_item_scrollable_panel.count())):
                self.add_item_scrollable_panel.itemAt(i).widget().setParent(None)

            dropdown_index = self.addItemTypeDropDown.currentIndex()
            selected_type_object = self.type_track_dict[dropdown_index]
            multiline_height = 200
            self.fields_inputs_dict["type"] = selected_type_object

            i = 0
            for x in selected_type_object.mandatory_atts:
                if x.name != "id" and x.name != "type":
                    new_textbox = QLineEdit()
                    new_multiline = QTextEdit()
                    new_multiline.setTabChangesFocus(True)
                    new_multiline.setMaximumHeight(multiline_height)
                    if x.is_many:
                        new_label = QLabel("<i><b>" + x.label + "</b></i><br><small>"+translations["SeperateValuesWithNewLine"][self.language])
                    else:
                        new_label = QLabel("<b>" + x.label + "</b>")
                    if x._transform is int:
                        new_label.setText(new_label.text() + "<br><small>" + translations["IntegerType"][self.language])
                    self.add_item_scrollable_panel.addWidget(new_label, i, 0)
                    if x.is_many:
                        self.add_item_scrollable_panel.addWidget(new_multiline, i, 1)
                        self.fields_inputs_dict[x] = new_multiline
                    else:
                        self.add_item_scrollable_panel.addWidget(new_textbox, i, 1)
                        self.fields_inputs_dict[x] = new_textbox
                i+=1

            for x in selected_type_object.optional_atts:
                new_textbox = QLineEdit()
                new_multiline = QTextEdit()
                new_multiline.setTabChangesFocus(True)
                new_multiline.setMaximumHeight(multiline_height)
                if x.is_many:
                    new_label = QLabel(
                        "<i>" + x.label + "</i><br><small>" + translations["SeperateValuesWithNewLine"][self.language])
                else:
                    new_label = QLabel(x.label)
                if x._transform is int:
                    new_label.setText(new_label.text() + "<br><small>" + translations["IntegerType"][self.language])
                self.add_item_scrollable_panel.addWidget(new_label, i, 0)
                if x.is_many:
                    self.add_item_scrollable_panel.addWidget(new_multiline, i, 1)
                    self.fields_inputs_dict[x] = new_multiline
                else:
                    self.add_item_scrollable_panel.addWidget(new_textbox, i, 1)
                    self.fields_inputs_dict[x] = new_textbox
                i += 1

        except Exception as e:
            pass


    def AddNewItemWindow(self, edit=None):
        try:
            dialog = QDialog()
            dialog.setStyleSheet('font-size: ' + str(self.fontsize) + 'pt;')
            dialog.setStyleSheet(self.stylesheet_to_use)
            self.AddItemDialogLayout = QGridLayout()
            dialog.setLayout(self.AddItemDialogLayout)
            dialog.setWindowTitle(translations["AddNewItemWindowTitle"][self.language])

            # Container Widget
            self.widget = QWidget()
            # Layout of Container Widget
            self.add_item_scrollable_panel = QGridLayout(self)
            self.widget.setLayout(self.add_item_scrollable_panel)


            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setMinimumWidth(480)
            scroll.setMinimumHeight(500)

            i = 0


            self.addItemTypeDropDown = QComboBox()
            self.addItemTypeDropDown.currentIndexChanged.connect(self.GenerateAddItemWidgets)
            self.AddItemDialogLayout.addWidget(self.addItemTypeDropDown, 2, 0)

            self.GenerateTypeDropDown()

            scroll.setWidget(self.widget)
            mainlabel = QLabel(
                "<b>"+translations["AddNewItemWindowHeading"][self.language]+"</b><br>"+translations["AddNewItemWindowText"][self.language])

            toto1 = QFrame()
            toto1.setFrameShape(QFrame.HLine)
            toto1.setFrameShadow(QFrame.Sunken)

            AddItemToCollection_Execute_btn = QPushButton(translations["AddItemToCollectionExecuteButton"][self.language])
            if edit:
                AddItemToCollection_Execute_btn.clicked.connect(partial(self.AddItem, edit=edit))
            else:
                AddItemToCollection_Execute_btn.clicked.connect(self.AddItem)

            self.addItemWarningLabel = QLabel("")
            self.addItemWarningLabel.setStyleSheet("color:red;")

            self.AddItemDialogLayout.addWidget(mainlabel, 0, 0)
            self.AddItemDialogLayout.addWidget(toto1, 1, 0)
            self.AddItemDialogLayout.addWidget(scroll, 3, 0)
            self.AddItemDialogLayout.addWidget(self.addItemWarningLabel, 4, 0)
            self.AddItemDialogLayout.addWidget(AddItemToCollection_Execute_btn, 5, 0)

            self.addItemWarningLabel.hide()

            print(self.fields_inputs_dict)

            if edit:
                print("uređivanje", edit)
                print(self.type_track_dict)
                dialog.setWindowTitle(translations["EditItemWindowTitle"][self.language])
                mainlabel.setParent(None)
                AddItemToCollection_Execute_btn.setText(translations["EditExecuteButton"][self.language])
                for itemtype in self.type_track_dict:
                    if self.col._data[edit]["type"] == itemtype.name:
                        self.addItemTypeDropDown.setCurrentIndex(self.type_track_dict.index(itemtype))
                        for itemfield, itemobject in self.fields_inputs_dict.items():
                            if itemfield != "type":
                                if itemfield.is_many:
                                    builder = []
                                    if self.col._data[edit][itemfield.name]:
                                        for each in self.col._data[edit][itemfield.name]:
                                            builder.append(str(each))
                                    itemobject.setText(str("\n".join(builder)))
                                else:
                                    itemobject.setText(str(self.col._data[edit][itemfield.name]))

            dialog.exec_()
        except Exception as e:
            print(e)

    def AddItem(self, edit=None):
        try:
            self.FireTempSave()
            #print(self.fields_inputs_dict)
            self.addItemWarningLabel.hide()
            self.addItemWarningLabel.setStyleSheet("color:"+self.warning_color+";")
            for x, y in self.fields_inputs_dict.items():
                if x != "type":
                    y.setStyleSheet("")
        except Exception as e:
            print(e, "100")
        try:
            item = {}
            type_of_pub = self.fields_inputs_dict["type"].name
            item["type"] = type_of_pub
        except Exception as e:
            print(e, "200")
        try:
            for x,y in self.fields_inputs_dict.items():
                if x != "type":
                    if x.is_many:
                        many_field = y.toPlainText()
                        if many_field:
                            many_field = many_field.split("\n")
                            item[x.name] = many_field
                        else:
                            item[x.name] = []
                    else:
                        if y.text():
                            item[x.name] = y.text()
                        else:
                            item[x.name] = None
        except Exception as e:
            print(e, "300")
        try:
            if edit:
                try:
                    item["id"] = edit
                    empty, invalid, faultyitem = self.col.editItem(iden=edit, **item, _transform=False)
                except Exception as e:
                    print(e)
            else:
                print(item)
                empty, invalid, faultyitem = self.col.addItem(**item)
        except Exception as e:
            print(e, "400")
        try:
            for x, y in self.fields_inputs_dict.items():
                if x != "type":
                    if x in empty:
                        y.setStyleSheet("border:1px solid "+self.warning_color+";")
                        req_mand = []
                        for x in empty:
                            req_mand.append(x.label)
                        req = ", ".join(req_mand)
                        self.addItemWarningLabel.setText(translations["FieldsAreRequiredWarning"][self.language].format(req))
                        self.addItemWarningLabel.show()

                    if x in invalid:
                        y.setStyleSheet("border:1px solid "+self.warning_color+";")
                        invalid_f = []
                        for x in invalid:
                            invalid_f.append(x.label)
                        inv = ", ".join(invalid_f)
                        self.addItemWarningLabel.setText(translations["InvalidFieldsWarning"][self.language].format(inv))
                        self.addItemWarningLabel.show()
            #print(self.col._data)
            self.RefreshCollectionView()
            if not empty and not invalid and not faultyitem:
                self.AddItemDialogLayout.parent().close()
            self.FireTempSave()
        except Exception as e:
            print(e, "500")

    def myprint(self, d):
        def find_key(d, key, value):
            for k, v in d.items():
                if isinstance(v, dict):
                    p = find_key(v, key, value)
                    if p:
                        return [k] + p
                elif v == value and k == key:
                    return [k]
        for k, v in sorted(d.items()):
            #print(k,v)
            parents = find_key(self.col._grouping_index, k, v)
            #print(parents)
            if type(v) is list:
                # print("{0} : {1}".format(k, v))
                if v:
                    self.level_of_group += 1
                    # sap = QLabel(str(k))
                    # sap.setStyleSheet("margin-left:{}px;".format(self.level_of_group*20))
                    # self.collection_layout.addWidget(sap, self.grouped_counter, 0)
                    # self.grouped_counter+=1
                    self.level_of_group += 1
                    if self.previousparent:
                        comparative = list(set(parents) - set(self.previousparent))
                        #print(comparative)
                        for parent in comparative:
                            labelo = QLabel("<h{}>".format(parents.index(parent)+3)+str(parent))
                            labelo.setStyleSheet("margin-left:{}px;color:{};".format(parents.index(parent)*15, self.accent_color))
                            self.collection_layout.addWidget(labelo, self.grouped_counter, 0)
                            self.grouped_counter += 1
                    else:
                        #print(parents)
                        for parent in parents:
                            labelo = QLabel("<h{}>".format(parents.index(parent)+3)+str(parent))
                            labelo.setStyleSheet("margin-left:{}px;color:{};".format(parents.index(parent) * 15, self.accent_color))
                            self.collection_layout.addWidget(labelo, self.grouped_counter, 0)
                            self.grouped_counter += 1

                    for each in v:
                        item = self.col._data[each]
                        item_chckbox = QCheckBox(str(item[self.col._view_field]), checkable=True)
                        item_chckbox.setStyleSheet("margin-left:{}px;padding:3px;".format(len(parents)*15))
                        item_chckbox.stateChanged.connect(partial(self.CollectionItemChecked, object=item_chckbox, itemid=item["id"]))
                        self.collection_layout.addWidget(item_chckbox, self.grouped_counter, 0)
                        self.checkboxes_handler[item["id"]] = item_chckbox
                        self.grouped_checkboxes_handler[item["id"]].append(item_chckbox)
                        self.grouped_counter+=1
                self.level_of_group = -1
            else:
                if v:
                    self.level_of_group += 1
                    self.myprint(v)
            self.previousparent = find_key(self.col._grouping_index, k, v)
            # if isinstance(v, list):
            #     self.myprint(v)
            # else:
            #     print("{0} : {1}".format(k, v))

    def RefreshCollectionView(self):
        try:
            for i in reversed(range(self.collection_layout.count())):
                self.collection_layout.itemAt(i).widget().setParent(None)
            i = 0
            if not self.col._grouping_index and not self.col._filtering_index:
                for x, y in self.col._data.items():
                    item_chckbox = QCheckBox(str(y[self.col._view_field]), checkable=True)
                    item_chckbox.setStyleSheet("padding:3px;")
                    item_chckbox.stateChanged.connect(
                        partial(self.CollectionItemChecked, object=item_chckbox, itemid=y["id"]))
                    self.collection_layout.addWidget(item_chckbox, i, 0)
                    self.checkboxes_handler[x] = item_chckbox
                    i += 1
            elif self.col._grouping_index:
                self.level_of_group = -1
                self.grouped_counter = 0
                self.grouped_checkboxes_handler = {}
                self.indent_handler_value_previous = None
                self.indent_level = 0
                self.indent_value_level = 0
                for x, y in self.col._data.items():
                    self.grouped_checkboxes_handler[x] = []
                self.previousparent = []
                self.myprint(self.col._grouping_index)
                if self.col._selected_items:
                    for selec in self.col._selected_items:
                        for each in self.grouped_checkboxes_handler[selec]:
                            each.setChecked(True)
                #print(self.grouped_checkboxes_handler)
            elif self.col._filtering_index and not self.col._grouping_index:
                for x, y in self.col._data.items():
                    if x in self.col._filtering_index:
                        item_chckbox = QCheckBox(str(y[self.col._view_field]), checkable=True)
                        item_chckbox.setStyleSheet("padding:3px;")
                        item_chckbox.stateChanged.connect(
                            partial(self.CollectionItemChecked, object=item_chckbox, itemid=y["id"]))
                        self.collection_layout.addWidget(item_chckbox, i, 0)
                        self.checkboxes_handler[x] = item_chckbox
                        i += 1

            for selected in self.col._selected_items:
                self.checkboxes_handler[selected].setChecked(True)
            count = len(self.col._recyclebin)
            self.garbage_btn.setText((str(count)))

        except Exception as e:
            print(e)
        # for x, y in self.col._data.items():
        #     print(type(x), x)
        # try:
        #     for i in reversed(range(self.collection_layout.count())):
        #         self.collection_layout.itemAt(i).widget().setParent(None)
        #     for x, y in self.col._data.items():
        #         print(x, y)
        #         item_chckbox = QCheckBox(str(y[self.col._view_field]), checkable=True)
        #         item_chckbox.stateChanged.connect(partial(self.CollectionItemChecked, object=item_chckbox, itemid=y["id"]))
        #         self.collection_layout.addWidget(item_chckbox, y["id"], 0)
        #         self.checkboxes_handler[x] = item_chckbox
        #         #print(self.checkboxes_handler)
        #     for selected in self.col._selected_items:
        #         self.checkboxes_handler[selected].setChecked(True)
        #     count = len(self.col._recyclebin)
        #     self.garbage_btn.setText(str(count))
        # except Exception as e:
        #     print(e)

    def RefreshView(self):
        try:
            for i in reversed(range(self.collection_layout.count())):
                self.collection_layout.itemAt(i).widget().setParent(None)
            ##AKO NEMA GRUPIRANJA
            i = 0
            if not self.col._grouping_index:
                for x, y in self.col._data.items():
                    item_chckbox = QCheckBox(str(y[self.col._view_field]), checkable=True)
                    item_chckbox.stateChanged.connect(
                        partial(self.CollectionItemChecked, object=item_chckbox, itemid=y["id"]))
                    self.collection_layout.addWidget(item_chckbox, i, 0)
                    self.checkboxes_handler[x] = item_chckbox
                    i += 1
            for selected in self.col._selected_items:
                self.checkboxes_handler[selected].setChecked(True)
            count = len(self.col._recyclebin)
            self.garbage_btn.setText((str(count)))

        except Exception as e:
            print(e)

    def CollectionItemChecked(self, object, itemid):
        try:
            if self.col._grouping_index:
                if object.isChecked():
                    self.checked_items_dict[itemid] = object
                    for each in self.grouped_checkboxes_handler[itemid]:
                        each.setStyleSheet(each.styleSheet() + "background-color:" + self.highlight_color + ";color:" + self.highlighted_text_color + ";")
                        each.setChecked(True)
                else:
                    self.checked_items_dict.pop(itemid, 0)
                    for each in self.grouped_checkboxes_handler[itemid]:
                        each.setStyleSheet(each.styleSheet() + self.transparent_background + "color:" + self.foreground_color + ";")
                        each.setChecked(False)
                    if itemid in self.col._selected_items:
                        self.col._selected_items.remove(itemid)
            else:
                if object.isChecked():
                    self.checked_items_dict[itemid] = object
                    object.setStyleSheet("background-color:"+self.highlight_color+";padding:3px;color:"+self.highlighted_text_color+";")
                else:
                    self.checked_items_dict.pop(itemid, 0)
                    object.setStyleSheet(self.transparent_background + "padding:3px;")
                    self.col._selected_items.remove(itemid)
            self.ShowDetails()
            #print(self.col._selected_items)
        except Exception as e:
            print(e)

        #print(self.col._selected_items)
        #print(self.checked_items_dict)

    def ShowDetails(self):
        for i in reversed(range(self.details_layout.count())):
            self.details_layout.itemAt(i).widget().setParent(None)
        #item_ids = []
        for x, y in self.checked_items_dict.items():
            if x not in self.col._selected_items:
                self.col._selected_items.append(x)

        if self.col._selected_items:
            self.delete_selected_button.show()
        else:
            self.delete_selected_button.hide()

        i = 1
        for id in self.col._selected_items:
            for x, y in self.col._data.items():
                if x == id:
                    for a, b in y.items():
                        for f in self.model_in_use.fields:
                            if a == f.name:
                                field_label = QLabel('<h5 style="color:'+self.accent_color+';">'+f.label)
                                self.details_layout.addWidget(field_label, i, 0, 1, 2)
                                i+=1
                                if f.is_many:
                                    str_list = list(filter(None, b))  # fastest
                                    if str_list:
                                        for e in b:
                                            value_label = QLabel(str(e))
                                            self.details_layout.addWidget(value_label, i, 0, 1, 2)
                                            i+=1
                                    else:
                                        field_label.hide()
                                else:
                                    if b:
                                        if a == "type":
                                            for w, y in self.model_in_use.types.items():
                                                if y.name == b:
                                                    value_label = QLabel(str(y.label))
                                                    self.details_layout.addWidget(value_label, i, 0, 1, 2)
                                                    i += 1
                                        else:
                                            value_label = QLabel(str(b))
                                            self.details_layout.addWidget(value_label, i, 0, 1, 2)
                                            i+= 1
                                    else:
                                        field_label.hide()
            edit_item_button = QPushButton(translations["EditItemButton"][self.language])
            edit_item_button.clicked.connect(partial(self.AddNewItemWindow, id))
            self.details_layout.addWidget(edit_item_button, i, 0)
            delete_item_button = QPushButton(translations["RemoveItemButton"][self.language])
            delete_item_button.setStyleSheet("background-color:"+self.warning_color+";color:"+self.highlighted_text_color+";")
            delete_item_button.clicked.connect(partial(self.ConfirmDelete, [id]))
            self.details_layout.addWidget(delete_item_button, i, 1)
            i+=1
            toto = QFrame()
            toto.setFrameShape(QFrame.HLine)
            toto.setFrameShadow(QFrame.Sunken)
            self.details_layout.addWidget(toto, i, 0, 1, 2)
            i+=1

    def ConfirmDelete(self, ids, selected=False):
        self.FireTempSave()
        if selected:
            self.col.removeItems(self.col._selected_items)
            temp_list = copy.deepcopy(self.col._selected_items)
            for ident in temp_list:
                self.checkboxes_handler[ident].setChecked(False)
                self.checkboxes_handler[ident].setParent(None)
        else:
            self.col.removeItems(ids)
            temp_list = copy.deepcopy(ids)
            for ident in temp_list:
                self.checkboxes_handler[ident].setChecked(False)
                self.checkboxes_handler[ident].setParent(None)
        self.RefreshCollectionView()
        self.FireTempSave()

    def RecycleBinWindow(self):
        dialog = QDialog()
        dialog.setStyleSheet('font-size: ' + str(self.fontsize) + 'pt;')
        dialog.setStyleSheet(self.stylesheet_to_use)
        self.RecycleBinLayout = QGridLayout()
        dialog.setLayout(self.RecycleBinLayout)
        dialog.setWindowTitle(translations["RecycleBinWindowTitle"][self.language])

        self.recycle_dict = {}
        self.selected_recycle_items = []
        self.all_recycle_items = []

        self.recycle_bin_scroll_widget = QWidget()
        # self.collection_view_widget.setStyleSheet("border:1px solid black;")
        # Layout of Container Widget
        self.rec_scroll_layout = QGridLayout(self)
        self.rec_scroll_layout.setAlignment(QtCore.Qt.AlignTop)
        self.recycle_bin_scroll_widget.setLayout(self.rec_scroll_layout)

        rec_scroll = QScrollArea()
        rec_scroll.setWidgetResizable(True)
        # scroll.setMaximumHeight(500)
        # scroll.setMaximumWidth(500)
        rec_scroll.setFrameStyle(QFrame.StyledPanel)

        rec_scroll.setWidget(self.recycle_bin_scroll_widget)

        self.RecycleBinLayout.addWidget(rec_scroll, 1, 0, 1, 2)

        toto = QFrame()
        toto.setFrameShape(QFrame.HLine)
        toto.setFrameShadow(QFrame.Sunken)

        self.RecycleBinLayout.addWidget(toto, 2, 0, 1, 2)

        self.PermaDeleteAll_button = QPushButton(translations["PermaDeleteAllButton"][self.language])
        self.PermaDeleteAll_button.setStyleSheet("background-color:"+self.warning_color+";color:"+self.highlighted_text_color+";")
        self.PermaDeleteAll_button.clicked.connect(partial(self.PermaDeleteItems, self.all_recycle_items))
        self.PermaDeleteSelected_button = QPushButton(translations["PermaDeleteSelectedButton"][self.language])
        self.PermaDeleteSelected_button.setStyleSheet("background-color:"+self.warning_color+";color:"+self.highlighted_text_color+";")
        self.PermaDeleteSelected_button.clicked.connect(partial(self.PermaDeleteItems, self.selected_recycle_items))
        self.RestoreAll_button = QPushButton(translations["RestoreAllButton"][self.language])
        self.RestoreAll_button.clicked.connect(partial(self.RestoreItems, self.all_recycle_items))
        self.RestoreSelected_button = QPushButton(translations["RestoreSelectedButton"][self.language])
        self.RestoreSelected_button.clicked.connect(partial(self.RestoreItems, self.selected_recycle_items))

        self.RecycleBinLayout.addWidget(self.PermaDeleteAll_button, 4, 0)
        self.RecycleBinLayout.addWidget(self.PermaDeleteSelected_button, 3, 0)
        self.RecycleBinLayout.addWidget(self.RestoreAll_button, 4, 1)
        self.RecycleBinLayout.addWidget(self.RestoreSelected_button, 3, 1)

        self.FillRecycleBinItems()

        self.RecycleBinButtonHandler()

        # achievements.CheckAchievement("FirstTrash", translations["FirstTrashAchievement"][self.language], translations["AchievementUnlocked"][self.language], self.tray_icon)

        dialog.exec_()

    def FillRecycleBinItems(self):
        try:
            for x, y in self.col._recyclebin.items():
                self.rec_scroll_layout.setAlignment(QtCore.Qt.AlignTop)
                item_checkbox = QCheckBox()
                item_checkbox.setText(str(y[self.col._view_field]))
                item_checkbox.stateChanged.connect(partial(self.CheckRecycleBinItem, x, item_checkbox))
                self.rec_scroll_layout.addWidget(item_checkbox, x, 0)
                delete_button = QPushButton(translations["PermaDeleteButton"][self.language])
                delete_button.setStyleSheet("background-color:"+self.warning_color+";color:"+self.highlighted_text_color+";")
                delete_button.clicked.connect(partial(self.PermaDeleteItems, [x]))
                restore_button = QPushButton(translations["RestoreButton"][self.language])
                restore_button.clicked.connect(partial(self.RestoreItems, [x]))
                self.rec_scroll_layout.addWidget(delete_button, x, 1)
                self.rec_scroll_layout.addWidget(restore_button, x, 2)
                self.recycle_dict[x] = [item_checkbox, delete_button, restore_button]
                self.all_recycle_items.append(x)
            self.CheckEmptyRecycleBin()
        except Exception as e:
            print(e)

    def CheckEmptyRecycleBin(self):
        if not self.col._recyclebin:
            self.rec_scroll_layout.setAlignment(QtCore.Qt.AlignCenter)
            bin_empty = QLabel(translations["RecycleBinEmptyLabel"][self.language])
            bin_empty.setStyleSheet("color:" + self.border_color + ";")
            self.rec_scroll_layout.addWidget(bin_empty, 0, 0)
            self.PermaDeleteAll_button.setEnabled(False)
            self.RestoreAll_button.setEnabled(False)

    def RestoreItems(self, ids):
        self.FireTempSave()
        ids = copy.deepcopy(ids)
        self.col.restoreItems(ids)
        for id in ids:
            for x, y in self.recycle_dict.items():
                if x == id:
                    for object in y:
                        object.setChecked(False)
                        object.setParent(None)
        #self.FillRecycleBinItems()
        self.CheckEmptyRecycleBin()
        self.RefreshCollectionView()
        self.FireTempSave()

    def PermaDeleteItems(self, ids):
        self.FireTempSave()
        ids = copy.deepcopy(ids)
        self.col.permaDelete(ids)
        for id in ids:
            for x, y in self.recycle_dict.items():
                if x == id:
                    for object in y:
                        object.setChecked(False)
                        object.setParent(None)
        self.CheckEmptyRecycleBin()
        self.FireTempSave()
        #self.FillRecycleBinItems()


    def RecycleBinButtonHandler(self):
        if self.selected_recycle_items:
            self.PermaDeleteSelected_button.setEnabled(True)
            self.RestoreSelected_button.setEnabled(True)
        else:
            self.PermaDeleteSelected_button.setEnabled(False)
            self.RestoreSelected_button.setEnabled(False)

    def CheckRecycleBinItem(self, ident, sender):
        self.FireTempSave()
        if sender.isChecked():
            self.selected_recycle_items.append(ident)
        else:
            self.selected_recycle_items.remove(ident)
        self.RecycleBinButtonHandler()
        self.FireTempSave()


    def EditColViewWindow(self):
        dialog = QDialog()
        dialog.setStyleSheet('font-size: ' + str(self.fontsize) + 'pt;')
        dialog.setStyleSheet(self.stylesheet_to_use)
        self.EditColViewLayout = QGridLayout()
        dialog.setLayout(self.EditColViewLayout)
        dialog.setWindowTitle(translations["EditColViewWindowTitle"][self.language])

        self.col_view_choice = QComboBox()

        self.fields_choice = {}

        i = 0
        for x in self.model_in_use.fields:
            if not x.is_many:
                self.col_view_choice.addItem(x.label)
                self.fields_choice[i] = x.name
                i += 1

        #print(temp_dict)

        self.EditColViewLayout.addWidget(self.col_view_choice, 0, 0)

        choose_button = QPushButton(translations["ChooseForCollectionView"][self.language])
        choose_button.clicked.connect(self.ApplyNewCollectionView)
        self.EditColViewLayout.addWidget(choose_button, 0, 1)

        dialog.exec_()

    def ApplyNewCollectionView(self):
        self.FireTempSave()
        for x, y in self.fields_choice.items():
            if x == self.col_view_choice.currentIndex():
                self.col._view_field = y
        self.RefreshCollectionView()
        self.EditColViewLayout.parent().close()
        self.FireTempSave()

    def FilteringWindow(self):
        dialog = QDialog()
        dialog.setStyleSheet('font-size: ' + str(self.fontsize) + 'pt;')
        dialog.setStyleSheet(self.stylesheet_to_use)
        dialog.setMinimumWidth(500)
        self.FilteringWindowLayout = QGridLayout()
        dialog.setLayout(self.FilteringWindowLayout)
        dialog.setWindowTitle(translations["FilterWindowTitle"][self.language])

        self.FilterIntOperators = [translations["IntFilter+"][self.language], translations["IntFilter-"][self.language], translations["IntFilter="][self.language]]
        self.FilterStrOperators = [translations["StrFilter+"][self.language], translations["StrFilter-"][self.language], translations["StrFilter="][self.language]]

        print(self.FilterIntOperators)
        print(self.FilterStrOperators)

        self.FiltersCounter = 0
        self.FiltersHandler = {}

        self.AddFilterHandle = QPushButton(translations["AddFilterButton"][self.language])
        self.AddFilterHandle.clicked.connect(self.AddFilterHandleFunc)
        self.RemoveFilters = QPushButton(translations["RemoveFiltersButtons"][self.language])
        self.RemoveFilters.clicked.connect(self.RemoveFiltersFunc)
        self.ApplyFilters = QPushButton(translations["ApplyFilters"][self.language])
        self.ApplyFilters.clicked.connect(self.ApplyFiltering)

        toto = QFrame()
        toto.setFrameShape(QFrame.HLine)
        toto.setFrameShadow(QFrame.Sunken)

        self.FilteringWindowLayout.addWidget(self.AddFilterHandle, 0, 0)
        self.FilteringWindowLayout.addWidget(self.RemoveFilters, 0, 1)
        self.FilteringWindowLayout.addWidget(self.ApplyFilters, 0, 2)
        self.FilteringWindowLayout.addWidget(toto, 1, 0, 1, 3)

        self.FiltersListWidget = QWidget()
        self.FiltersListLayout = QGridLayout()
        self.FiltersListWidget.setLayout(self.FiltersListLayout)
        self.FilteringWindowLayout.addWidget(self.FiltersListWidget, 2, 0, 1, 3)

        print(self.FiltersDict)
        print(self.FiltersCounter)
        print(self.FiltersHandler)

        if self.FiltersDict:
            for key, value in self.FiltersDict.items():
                self.AddFilterHandleFunc(edit=value)

        dialog.exec_()

    def RemoveFiltersFunc(self):
        self.FireTempSave()
        self.col._filtering_index = []
        self.FiltersDict = {}
        self.RefreshCollectionView()
        self.FilteringWindowLayout.parent().close()
        self.FireTempSave()

    def ApplyFiltering(self):
        try:
            self.FireTempSave()
            self.FiltersDict = {}
            ops = ["+", "-", "="]
            for x, y in self.FiltersHandler.items():
                self.FiltersDict[x] = {}
                if self.filter_fields_list[self.FiltersHandler[x]["field"].currentIndex()]._transform is int:
                    self.FiltersDict[x]["type"] = int
                    if self.FiltersHandler[x]["input"].text():
                        self.FiltersDict[x]["value"] = int(self.FiltersHandler[x]["input"].text())
                    else:
                        self.FiltersDict[x]["value"] = 0
                else:
                    self.FiltersDict[x]["type"] = str
                    self.FiltersDict[x]["value"] = self.FiltersHandler[x]["input"].text()
                self.FiltersDict[x]["field"] = self.filter_fields_list[self.FiltersHandler[x]["field"].currentIndex()].name
                self.FiltersDict[x]["operator"] = ops[self.FiltersHandler[x]["operator"].currentIndex()]
            print(self.FiltersDict)
            self.col.filterCollection(self.FiltersDict)
            print(self.col._filtering_index)
            self.RefreshCollectionView()
            self.FilteringWindowLayout.parent().close()
            self.FireTempSave()
        except Exception as e:
            print(e)

    def AddFilterHandleFunc(self, edit=None):
        try:
            self.FiltersHandler[self.FiltersCounter] = {}
            model_field = QComboBox()
            self.filter_fields_list = []
            for field in self.col.model.fields:
                if field.name != "id":
                    self.filter_fields_list.append(field)
                    model_field.addItem(field.label)
            line_input = QLineEdit()
            line_input.setPlaceholderText(translations["FilterParam"][self.language])
            self.FiltersListLayout.addWidget(model_field, self.FiltersCounter, 1)
            self.FiltersListLayout.addWidget(line_input, self.FiltersCounter, 3)
            self.FiltersHandler[self.FiltersCounter]["field"] = model_field
            self.FiltersHandler[self.FiltersCounter]["input"] = line_input
            model_field.currentIndexChanged.connect(partial(self.CheckFilterType, self.FiltersCounter))
            self.CheckFilterType(self.FiltersCounter)
            if self.FiltersCounter > 0:
                and_label = QLabel(translations["FilterAnd"][self.language])
            else:
                and_label = QLabel(translations["FilterIf"][self.language])
            and_label.setStyleSheet("padding-right:10px;")
            self.FiltersListLayout.addWidget(and_label, self.FiltersCounter, 0)

            if edit:
                for ffield in self.filter_fields_list:
                    if ffield.name == edit["field"]:
                        model_field.setCurrentIndex(self.filter_fields_list.index(ffield))
                line_input.setText(str(edit["value"]))
                self.CheckFilterType(self.FiltersCounter, edit=edit)


            self.FiltersCounter+=1
        except Exception as e:
            print(e)

    def CheckFilterType(self, id, edit=None):
        try:
            ops = ["+", "-", "="]
            if self.filter_fields_list[self.FiltersHandler[id]["field"].currentIndex()]._transform is int:
                operator_combo = QComboBox()
                for each in self.FilterIntOperators:
                    operator_combo.addItem(each)
                self.FiltersListLayout.addWidget(operator_combo, id, 2)
                self.FiltersHandler[id]["operator"] = operator_combo
                if edit:
                    operator_combo.setCurrentIndex(ops.index(edit["operator"]))
            else:
                operator_combo = QComboBox()
                for each in self.FilterStrOperators:
                    operator_combo.addItem(each)
                self.FiltersListLayout.addWidget(operator_combo, id, 2)
                self.FiltersHandler[id]["operator"] = operator_combo
                if edit:
                    operator_combo.setCurrentIndex(ops.index(edit["operator"]))
        except Exception as e:
            print(e)

    def GroupingWindow(self):
        #self.col.NewGrouping(["jednostavni_autori", "jednostavni_godina"])
        self.grouping_handler = []
        self.grouping_fields_object_list = []
        self.grouping_elements_counter = 1
        dialog = QDialog()
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet('font-size: ' + str(self.fontsize) + 'pt;')
        dialog.setStyleSheet(self.stylesheet_to_use)
        self.GroupingWindowLayout = QGridLayout()
        dialog.setLayout(self.GroupingWindowLayout)
        dialog.setWindowTitle(translations["GroupingWindowTitle"][self.language])

        self.AddGroupingLevelButton = QPushButton(translations["AddGroupingLevelButton"][self.language])
        self.AddGroupingLevelButton.clicked.connect(self.AddGroupingLevel)
        self.GroupingWindowLayout.addWidget(self.AddGroupingLevelButton, 0, 0)
        self.RemoveAllGroupParamsButton = QPushButton(translations["ClearGroupingLevels"][self.language])
        self.RemoveAllGroupParamsButton.clicked.connect(self.ClearGroupingParameters)
        self.GroupingWindowLayout.addWidget(self.RemoveAllGroupParamsButton, 0, 1)
        self.ApplyGroupingParamsButton = QPushButton(translations["ApplyGroupingParams"][self.language])
        self.ApplyGroupingParamsButton.clicked.connect(self.ApplyGrouping)
        self.GroupingWindowLayout.addWidget(self.ApplyGroupingParamsButton, 0, 2)

        if self.col._grouping_fields:
            for each in self.col._grouping_fields:
                self.AddGroupingLevel(set=each)

        dialog.exec_()

    def ApplyGrouping(self):
        # self.col._grouping_field = []
        self.FireTempSave()
        params = []
        for x in self.grouping_handler:
            params.append(self.grouping_fields_object_list[x.currentIndex()].name)
            # self.col._grouping_field.append(self.grouping_fields_object_list[x.currentIndex()].name)
        self.col.NewGrouping(params)
        print(self.col._grouping_index)
        self.RefreshCollectionView()
        self.GroupingWindowLayout.parent().close()
        self.FireTempSave()

    def AddGroupingLevel(self, set=None):
        GroupByFieldBox = QComboBox()
        for x in self.model_in_use.fields:
            if x.name != "id":
                GroupByFieldBox.addItem(x.label)
                self.grouping_fields_object_list.append(x)
        GroupingLevelLabel = QLabel(translations["GroupingLevel"][self.language] + " " + str(self.grouping_elements_counter) + ": ")
        self.GroupingWindowLayout.addWidget(GroupingLevelLabel, self.grouping_elements_counter, 0, 1, 2)
        self.GroupingWindowLayout.addWidget(GroupByFieldBox, self.grouping_elements_counter, 1, 1, 2)
        self.grouping_handler.append(GroupByFieldBox)
        self.grouping_elements_counter += 1

        if set:
            for xfield in self.grouping_fields_object_list:
                if xfield.name == set:
                    GroupByFieldBox.setCurrentIndex(self.grouping_fields_object_list.index(xfield))

    def ClearGroupingParameters(self):
        self.FireTempSave()
        self.col._grouping_index = {}
        self.CurrentGroupingParams = []
        self.RefreshCollectionView()
        self.GroupingWindowLayout.parent().close()
        self.FireTempSave()

    def ApplyGroupingParameters(self):
        pass

    def AppereanceWindow(self):

        dialog = QDialog()
        self.AppereanceWindowLayout = QGridLayout()
        dialog.setLayout(self.AppereanceWindowLayout)
        dialog.setWindowTitle(translations["AppereanceWindowTitle"][self.language])
        dialog.setStyleSheet(self.stylesheet_to_use)

        choose_theme_label = QLabel(translations["AppereanceWindowChooseThemeLabel"][self.language])
        self.AppereanceWindowLayout.addWidget(choose_theme_label, 1, 0)

        self.choose_theme_combo = QComboBox()
        self.choose_theme_combo.addItem(self.theme)
        for x, y in self.themes_dict.items():
            if x != self.theme:
                self.choose_theme_combo.addItem(x)
        #self.choose_theme_combo.currentIndexChanged.connect(partial(self.ChangeTheme, dialog))
        self.choose_theme_combo.currentIndexChanged.connect(self.PreviewTheme)
        self.AppereanceWindowLayout.addWidget(self.choose_theme_combo, 1, 1)
        self.apply_button = QPushButton(translations["ApplyGeneral"][self.language])
        self.apply_button.clicked.connect(partial(self.ChangeTheme, dialog, apply=True))
        self.AppereanceWindowLayout.addWidget(self.apply_button, 1, 2)

        toto = QFrame()
        toto.setFrameShape(QFrame.HLine)
        toto.setFrameShadow(QFrame.Sunken)

        self.AppereanceWindowLayout.addWidget(toto, 2, 0, 1, 3)

        self.newtheme_widget = QWidget()
        # Layout of Container Widget
        self.newtheme_panel = QGridLayout()
        self.newtheme_widget.setLayout(self.newtheme_panel)

        self.AppereanceWindowLayout.addWidget(self.newtheme_widget, 3, 0, 1, 3)

        self.previewthemelabelstylesheet = "color:#888;text-shadow: 2px 2px #ff0000;padding:4px;"

        self.colors_labels = ["BackgroundColor", "ForegroundColor", "HighlightColor", "HighlightedTextColor", "BorderColor", "AccentColor", "WarningColor"]

        self.colors_handler_dict = {}

        self.preview_new_theme_state = False

        self.new_theme_name = QLineEdit()
        self.new_theme_name.setPlaceholderText(translations["NewThemeNameTextBox"][self.language])
        self.newtheme_panel.addWidget(self.new_theme_name, 0, 0, 1, 2)

        try:
            i = 1
            for color_label in self.colors_labels:
                self.new_color_label = QLabel(translations[color_label][self.language])
                self.new_color_label.setStyleSheet(self.previewthemelabelstylesheet)
                self.newtheme_panel.addWidget(self.new_color_label, i, 0)
                self.new_color_button = QPushButton(translations["ChooseColorButton"][self.language])
                self.new_color_button.clicked.connect(partial(self.ChooseColor, color_label))
                self.newtheme_panel.addWidget(self.new_color_button, i, 1)
                self.colors_handler_dict[color_label] = {"label_object": self.new_color_label, "button_object": self.new_color_button, "color_code": self.background_color}
                i += 1
        except Exception as e:
            print(e)

        self.preview_new_theme_chckbox = QCheckBox(translations["PreviewNewTheme"][self.language], checkable=True)
        self.preview_new_theme_chckbox.setStyleSheet("margin:10px;")
        self.preview_new_theme_chckbox.stateChanged.connect(self.ChangePreviewNew)
        self.newtheme_panel.addWidget(self.preview_new_theme_chckbox, i, 0)
        i += 1

        self.add_new_theme_button = QPushButton(translations["AddNewThemeButton"][self.language])
        self.add_new_theme_button.clicked.connect(self.AddNewTheme)
        self.newtheme_panel.addWidget(self.add_new_theme_button, i, 0)

        self.add_and_apply_theme_button = QPushButton(translations["AddAndApplyNewTheme"][self.language])
        self.add_and_apply_theme_button.clicked.connect(self.AddAndApplyTheme)
        self.newtheme_panel.addWidget(self.add_and_apply_theme_button, i, 1)

        dialog.exec_()

        self.ChangeTheme(dialog, apply=False)

    def AddAndApplyTheme(self):
        self.new_theme_to_store = {}
        for x, y in self.colors_handler_dict.items():
            self.new_theme_to_store[x] = y["color_code"]
        self.themes_dict[self.new_theme_name.text()] = self.new_theme_to_store
        with open("themes.json", "w") as fp:
            json.dump(self.themes_dict, fp)
        self.choose_theme_combo.addItem(self.new_theme_name.text())
        self.choose_theme_combo.setCurrentText(self.new_theme_name.text())
        self.apply_button.click()

    def AddNewTheme(self):
        self.new_theme_to_store = {}
        for x, y in self.colors_handler_dict.items():
            self.new_theme_to_store[x] = y["color_code"]
        self.themes_dict[self.new_theme_name.text()] = self.new_theme_to_store
        with open("themes.json", "w") as fp:
            json.dump(self.themes_dict, fp)
        self.choose_theme_combo.addItem(self.new_theme_name.text())

    def ChangePreviewNew(self):
        if self.preview_new_theme_chckbox.isChecked():
            self.preview_new_theme_state = True
            self.PreviewNewTheme()
        else:
            self.preview_new_theme_state = False
            self.PreviewTheme()

    def ChooseColor(self, color):
        color_dialog = QColorDialog()
        self.colors_handler_dict[color]["color_code"] = color_dialog.getColor().name()
        self.colors_handler_dict[color]["label_object"].setStyleSheet(self.previewthemelabelstylesheet + "background-color:"+self.colors_handler_dict[color]["color_code"]+";")
        if self.preview_new_theme_state:
            self.PreviewNewTheme()

    def PreviewNewTheme(self):
        self.new_theme_to_preview = {}
        for x, y in self.colors_handler_dict.items():
            self.new_theme_to_preview[x] = y["color_code"]
        self.ApplyStylesheet(previewNew=True)

    def ChangeTheme(self, dialogtochange, apply=True):
        if apply:
            self.theme = self.choose_theme_combo.currentText()
        self.ApplyStylesheet()
        self.ApplyStylesheetToMenus()
        dialogtochange.setStyleSheet(self.stylesheet_to_use)

    def PreviewTheme(self):
        self.previewtheme = self.choose_theme_combo.currentText()
        self.ApplyStylesheet(preview=True)

    def FormatMapperHandler(self, format):
        if format == "CSV":
            self.CSVWindow()
        elif format == "BibTeX":
            self.BIBTEXWindow()
        elif format == "MARC":
            self.UNIMARCWindow()

    def CSVWindow(self):
        dialog = QDialog()
        self.CSVWindowLayout = QGridLayout()
        dialog.setLayout(self.CSVWindowLayout)
        dialog.setWindowTitle(translations["CSVWindowTitle"][self.language])
        dialog.setStyleSheet(self.stylesheet_to_use)

        self.CSVModelCombo = QComboBox()
        for x, y in models.items():
            if x == self.set_model:
                self.CSVModelCombo.addItem(x)

        for x, y in models.items():
            if x != self.set_model:
                self.CSVModelCombo.addItem(x)

        self.CSVModelCombo.currentIndexChanged.connect(self.ReadMappersForModel)

        self.CSVWindowLayout.addWidget(self.CSVModelCombo, 0, 0)

        self.mappers_for_current_model_scroll = QWidget()
        self.mappers_layout = QGridLayout(self)
        self.mappers_layout.setAlignment(QtCore.Qt.AlignTop)
        self.mappers_for_current_model_scroll.setLayout(self.mappers_layout)
        map_scroll = QScrollArea()
        map_scroll.setWidgetResizable(True)
        map_scroll.setMinimumHeight(300)
        map_scroll.setMinimumWidth(300)
        map_scroll.setFrameStyle(QFrame.StyledPanel)
        map_scroll.setWidget(self.mappers_for_current_model_scroll)
        self.CSVWindowLayout.addWidget(map_scroll, 1, 0)

        self.model_object = models[self.CSVModelCombo.currentText()]["object"]


        self.ReadMappersForModel()

        toto = QFrame()
        toto.setFrameShape(QFrame.HLine)
        toto.setFrameShadow(QFrame.Sunken)

        dialog.exec_()

    def ReadMappersForModel(self):
        for i in reversed(range(self.mappers_layout.count())):
            self.mappers_layout.itemAt(i).widget().setParent(None)
        self.mapping_csv_dict_for_cur_model = {}
        self.model_object = models[self.CSVModelCombo.currentText()]["object"]
        #print(self.model_object.name)

        self.add_mapper_for_this_model_button = QPushButton(translations["CSVAddMapperForModel"][self.language])
        self.add_mapper_for_this_model_button.clicked.connect(
            partial(self.CSVMapperWindow, new=True, model_in_use=self.model_object))
        self.CSVWindowLayout.addWidget(self.add_mapper_for_this_model_button, 2, 0)
        #print(model_object.name)
        self.CSV_scroll_object_handler = {}
        try:
            with open("models/"+self.model_object.name+"/mappers/csv.json") as json_data:
                self.mapping_csv_dict_for_cur_model = json.load(json_data)
            i = 0
            for x, y in self.mapping_csv_dict_for_cur_model.items():
                mapping_label = QLabel(x)
                edit_button = QPushButton(translations["CSVMappingEditButton"][self.language])
                edit_button.clicked.connect(partial(self.CSVMapperWindow, new=False, model_in_use=self.model_object, mapper=x))
                delete_button = QPushButton(translations["CSVMappingDeleteButton"][self.language])
                delete_button.setStyleSheet("background-color:"+self.warning_color+";color:"+self.highlighted_text_color+";")
                delete_button.clicked.connect(partial(self.DeleteCSVMapping, i, x))
                self.mappers_layout.addWidget(mapping_label, i, 0)
                self.mappers_layout.addWidget(edit_button, i, 1)
                self.mappers_layout.addWidget(delete_button, i, 2)
                self.CSV_scroll_object_handler[i] = {"label": mapping_label, "edit": edit_button, "delete": delete_button}
                i += 1
        except:
            no_mappings_label = QLabel(translations["CSVNoMappingsLabel"][self.language])
            no_mappings_label.setStyleSheet("color:"+self.border_color+";")
            self.mappers_layout.addWidget(no_mappings_label, 0, 0)

    def DeleteCSVMapping(self, pos, mapping):
        del self.mapping_csv_dict_for_cur_model[mapping]
        #print(self.mapping_csv_dict_for_cur_model)
        #print(self.model_object.name)
        for x, y in self.CSV_scroll_object_handler[pos].items():
            y.setParent(None)
        with open("models/" + self.model_object.name + "/mappers/csv.json", 'w') as fp:
            json.dump(self.mapping_csv_dict_for_cur_model, fp)

    def CSVMapperWindow(self, new=True, model_in_use=None, mapper=None):
        try:
            dialog = QDialog()
            self.CSVMapperWindowLayout = QGridLayout()
            dialog.setLayout(self.CSVMapperWindowLayout)
            if new:
                dialog.setWindowTitle(translations["NewCSVTabTitle"][self.language] + " ("+model_in_use.name+")")
            else:
                dialog.setWindowTitle(mapper + " ("+model_in_use.name+")")
            dialog.setStyleSheet(self.stylesheet_to_use)
            dialog.setMinimumWidth(800)


            CSVMapperWindowMenu = QMenuBar()
            CSVMapperWindowMenu.addAction(translations["CSVAddFieldButton"][self.language], partial(self.AddCSVField))
            CSVMapperWindowMenu.addAction(translations["CSVAddFieldsFromFileButton"][self.language], partial(self.CSVFieldsFromFile))
            CSVMapperWindowMenu.addAction(translations["CSVAddTypeButton"][self.language], partial(self.AddCSVType))
            CSVMapperWindowMenu.addAction(translations["CSVSaveChangesButton"][self.language], partial(self.SaveCSVMappingInfo, model_in_use))
            self.CSVMapperWindowLayout.setMenuBar(CSVMapperWindowMenu)

            csv_mapping_name_label = QLabel(translations["CSVMapperName"][self.language])
            self.csv_mapping_name_text = QLineEdit()
            self.CSVMapperWindowLayout.addWidget(csv_mapping_name_label, 0, 0)
            self.CSVMapperWindowLayout.addWidget(self.csv_mapping_name_text, 0, 1)

            csv_delimiter_label = QLabel(translations["DelimiterLabel"][self.language])
            self.csv_delimiter_text = QLineEdit()
            self.csv_delimiter_text.setPlaceholderText(translations["CSVDelimiterPlaceholder"][self.language])
            self.CSVMapperWindowLayout.addWidget(csv_delimiter_label, 1, 0)
            self.CSVMapperWindowLayout.addWidget(self.csv_delimiter_text, 1, 1)
            self.csv_tab_delimited_checkbox = QCheckBox(translations["CSVTabDelimitedBox"][self.language])
            #self.CSVMapperWindowLayout.addWidget(self.csv_tab_delimited_checkbox, 1, 2)

            toto = QFrame()
            toto.setFrameShape(QFrame.HLine)
            toto.setFrameShadow(QFrame.Sunken)

            self.CSVMapperWindowLayout.addWidget(toto, 2, 0, 1, 2)

            csv_fields_label = QLabel(translations["CSVFieldsLabel"][self.language])
            csv_types_label = QLabel(translations["CSVTypesLabel"][self.language])
            self.CSVMapperWindowLayout.addWidget(csv_fields_label, 3, 0)
            self.CSVMapperWindowLayout.addWidget(csv_types_label, 3, 1)

            self.CSV_scroll_widgets = {}

            self.GenerateCSVScrollWidgets(["field_scroller", "type_scroller"], 4, 0)

            self.csv_field_iterator = 0
            self.csv_type_iterator = 0
            self.csv_field_indexes = []
            self.csv_fields_controller = {}
            self.csv_type_indexes = []
            self.csv_type_controller = {}
            for field in model_in_use.fields:
                if field.name != "id":
                    if field not in self.csv_field_indexes:
                        self.csv_field_indexes.append(field)

            for a, b in model_in_use.types.items():
                if b not in self.csv_type_indexes:
                    self.csv_type_indexes.append(b)

            if not new:
                self.csv_mapping_name_text.setText(mapper)
                self.csv_delimiter_text.setText(self.mapping_csv_dict_for_cur_model[mapper]["delimiter"])
                for x, y in self.mapping_csv_dict_for_cur_model[mapper]["fields_map"].items():
                    for field in self.csv_field_indexes:
                        if field.name == y:
                            field_index = self.csv_field_indexes.index(field)
                    self.AddCSVField(set_csv_field=x, set_model_field=field_index)
                for x, y in self.mapping_csv_dict_for_cur_model[mapper]["type_map"].items():
                    for type in self.csv_type_indexes:
                        if type.name == y:
                            type_index = self.csv_type_indexes.index(type)
                    self.AddCSVType(set_csv_type=x, set_model_type=type_index)

            self.one_type_checkbox = QCheckBox(translations["CSVMapAllToOneType"][self.language])
            self.one_type_checkbox.stateChanged.connect(self.ChangeOneType)
            self.CSVMapperWindowLayout.addWidget(self.one_type_checkbox, 5, 1)
            self.one_type_combo = QComboBox()
            for type in self.csv_type_indexes:
                self.one_type_combo.addItem(type.label)
            self.CSVMapperWindowLayout.addWidget(self.one_type_combo, 6, 1)

            if not new:
                if self.mapping_csv_dict_for_cur_model[mapper]["one_type"]:
                    self.one_type_checkbox.setChecked(True)
                    for type in self.csv_type_indexes:
                        if self.mapping_csv_dict_for_cur_model[mapper]["one_type"] == type.name:
                            self.one_type_combo.setCurrentIndex(self.csv_type_indexes.index(type))

            dialog.exec_()
        except Exception as e:
            print(e)

    def SaveCSVMappingInfo(self, model):
        print(model.name)
        try:
            mappingname = self.csv_mapping_name_text.text()

            temp_delimiter = self.csv_delimiter_text.text()
            temp_one_type = ""
            if self.one_type_checkbox.isChecked():
                one_type_combo_index = self.one_type_combo.currentIndex()
                temp_one_type = self.csv_type_indexes[one_type_combo_index].name

            #print(self.csv_fields_controller)
            temp_fields_map_dict = {}
            for x, y in self.csv_fields_controller.items():
                csv_field = y["csv_field_box"].text()
                model_field_index = y["model_field_combo"].currentIndex()
                model_field = self.csv_field_indexes[model_field_index].name
                temp_fields_map_dict[csv_field] = model_field
            #print(temp_fields_map_dict)

            temp_types_map_dict = {}
            for x, y in self.csv_type_controller.items():
                csv_type = y["csv_type_box"].text()
                model_type_index = y["model_type_combo"].currentIndex()
                model_type = self.csv_type_indexes[model_type_index].name
                temp_types_map_dict[csv_type] = model_type
            #print(temp_types_map_dict)

            self.mapping_csv_dict_for_cur_model[mappingname] = {"delimiter": temp_delimiter, "one_type": temp_one_type, "fields_map": temp_fields_map_dict, "type_map": temp_types_map_dict}

            # self.mapping_csv_dict_for_cur_model[mappingname]["fields_map"] = temp_fields_map_dict
            # self.mapping_csv_dict_for_cur_model[mappingname]["type_map"] = temp_types_map_dict

            with open("models/"+model.name+"/mappers/csv.json", 'w') as fp:
                json.dump(self.mapping_csv_dict_for_cur_model, fp)

            self.ReadMappersForModel()

            #print(self.mapping_csv_dict_for_cur_model)

            #print(self.mapping_csv_dict_for_cur_model)
            ## NOVO MAPIRANJE

            self.CSVMapperWindowLayout.parent().close()

        except Exception as e:
            print(e)

    def remove_bom(self, line):
        return line[3:] if line.startswith(codecs.BOM_UTF8) else line

    def CSVFieldsFromFile(self):
        try:
            if self.csv_delimiter_text.text():
                delmt = self.csv_delimiter_text.text()
            else:
                delmt = "\t"
            open_file = QFileDialog()
            open_file.setFileMode(QFileDialog.ExistingFiles)
            file_to_open = open_file.getOpenFileName(self)
            fields = []
            with open(file_to_open[0], newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=delmt)
                for row in reader:
                    for value in row:
                        fields.append(value)
                    break
            for field in fields:
                self.AddCSVField(set_csv_field=field, set_model_field=0)
        except Exception as e:
            self.OKdialog(translations["CSVReadFromFileError"][self.language])
            print(e)

    def ChangeOneType(self):
        try:
            if self.one_type_checkbox.isChecked():
                for i in reversed(range(self.CSV_scroll_widgets["type_scroller"].count())):
                    self.CSV_scroll_widgets["type_scroller"].itemAt(i).widget().setDisabled(True)
            else:
                for i in reversed(range(self.CSV_scroll_widgets["type_scroller"].count())):
                    self.CSV_scroll_widgets["type_scroller"].itemAt(i).widget().setDisabled(False)
        except Exception as e:
            print(e)

    def AddCSVType(self, set_csv_type=None, set_model_type=None):
        csv_type = QLineEdit()
        csv_type.setPlaceholderText(translations["CSVTypePlaceholder"][self.language])
        self.CSV_scroll_widgets["type_scroller"].addWidget(csv_type, self.csv_type_iterator, 0)

        model_types_combo = QComboBox()
        for type in self.csv_type_indexes:
            model_types_combo.addItem(type.label)
        self.CSV_scroll_widgets["type_scroller"].addWidget(model_types_combo, self.csv_type_iterator, 1)
        csv_remove_type = QPushButton(translations["CSVRemove"][self.language])
        csv_remove_type.setStyleSheet("background-color:"+self.warning_color+";color:"+self.highlighted_text_color+";")
        csv_remove_type.clicked.connect(partial(self.RemoveCSVType, self.csv_type_iterator))
        self.CSV_scroll_widgets["type_scroller"].addWidget(csv_remove_type, self.csv_type_iterator, 2)

        self.csv_type_controller[self.csv_type_iterator] = {"csv_type_box": csv_type, "model_type_combo": model_types_combo, "deleter": csv_remove_type}

        if set_csv_type:
            csv_type.setText(set_csv_type)
            model_types_combo.setCurrentIndex(set_model_type)

        self.csv_type_iterator += 1

    def AddCSVField(self, set_csv_field=None, set_model_field=None):
        csv_field = QLineEdit()
        csv_field.setPlaceholderText(translations["CSVFieldPlaceholder"][self.language])
        self.CSV_scroll_widgets["field_scroller"].addWidget(csv_field, self.csv_field_iterator, 0)

        model_fields_combo = QComboBox()
        for field in self.csv_field_indexes:
            model_fields_combo.addItem(field.label)
        self.CSV_scroll_widgets["field_scroller"].addWidget(model_fields_combo, self.csv_field_iterator, 1)

        csv_remove_field = QPushButton(translations["CSVRemove"][self.language])
        csv_remove_field.setStyleSheet("background-color:"+self.warning_color+";color:"+self.highlighted_text_color+";")
        csv_remove_field.clicked.connect(partial(self.RemoveCSVField, self.csv_field_iterator))
        self.CSV_scroll_widgets["field_scroller"].addWidget(csv_remove_field, self.csv_field_iterator, 2)

        self.csv_fields_controller[self.csv_field_iterator] = {"csv_field_box": csv_field, "model_field_combo": model_fields_combo, "deleter": csv_remove_field}

        if set_csv_field:
            csv_field.setText(set_csv_field)
            model_fields_combo.setCurrentIndex(set_model_field)

        self.csv_field_iterator += 1

    def RemoveCSVField(self, number):
        for x, y in self.csv_fields_controller[number].items():
            y.setParent(None)
        del self.csv_fields_controller[number]

    def RemoveCSVType(self, number):
        for x, y in self.csv_type_controller[number].items():
            y.setParent(None)
        del self.csv_type_controller[number]

    def GenerateCSVScrollWidgets(self, names, position, iterator):
        for name in names:
            csv_scroll_widget = QWidget()
            scroll_layout = QGridLayout(self)
            scroll_layout.setAlignment(QtCore.Qt.AlignTop)
            csv_scroll_widget.setLayout(scroll_layout)
            scroller = QScrollArea()
            scroller.setWidgetResizable(True)
            scroller.setFrameStyle(QFrame.StyledPanel)
            scroller.setWidget(csv_scroll_widget)
            scroller.setMinimumHeight(300)
            self.CSVMapperWindowLayout.addWidget(scroller, position, iterator)
            self.CSV_scroll_widgets[name] = scroll_layout
            iterator += 1

    def NewStyleWindow(self, edit=False, model=None, cit=None):
        try:
            #PROZOR
            dialog = QDialog()
            self.NewStyleWindowLayout = QGridLayout()
            dialog.setLayout(self.NewStyleWindowLayout)
            dialog.setWindowTitle(translations["NewCitationStyleWindowTitle"][self.language])
            dialog.setStyleSheet(self.stylesheet_to_use)

            toto = QFrame()
            toto.setFrameShape(QFrame.HLine)
            toto.setFrameShadow(QFrame.Sunken)

            self.CitationStyleName = QLineEdit()
            self.CitationStyleName.setPlaceholderText(translations["CitationStyleName"][self.language])
            self.CitationStyleModelChoose = QComboBox()
            self.CitationStyleTypeChoose = QComboBox()
            self.CitationStyleModelFieldsChoose = QComboBox()
            self.CitationStyleAddFieldToSyntax = QPushButton(translations["CitationStyleAddToSyntax"][self.language])
            self.CitationStyleSyntaxBox = QTextEdit()
            self.CitationStyleSyntaxBox.setPlaceholderText(translations["CitationStyleSyntaxBoxPlaceholder"][self.language])
            self.CitationStylePreviewBox = QTextEdit()
            self.CitationStylePreviewBox.setPlaceholderText(translations["CitationStylePreviewBoxPlaceholder"][self.language])
            self.CitationStyleMultipleDelimiterLabel = QLabel(translations["CitationStyleMultipleDelimiterLabel"][self.language])
            self.CitationStyleMultipleDelimiterText = QLineEdit()
            self.CitationStyleLastDelimiterLabel = QLabel(translations["CitationStyleLastDelimiterLabel"][self.language])
            self.CitationStyleLastDelimiterText = QLineEdit()
            self.CitationStyleSaveButton = QPushButton(translations["CitationStyleSave"][self.language])


            self.CitationStyleModelOrder = []
            self.CitationStyleTypeOrder = []
            self.CitationStyleFieldOrder = []
            self.NewStyleDict = {"rules": {}, "separators": {}}

            self.CitationStylePreviewBox.setDisabled(True)
            self.CitationStyleAddFieldToSyntax.clicked.connect(self.AddFieldToSyntax)

            self.CitationStyleModelChoose.currentIndexChanged.connect(self.CitationModelChangeHandler)
            self.CitationStyleTypeChoose.currentIndexChanged.connect(self.CitationTypeChangeHandler)
            self.CitationStyleSyntaxBox.textChanged.connect(self.TemporaryChanges)
            self.CitationStyleMultipleDelimiterText.textChanged.connect(self.TemporaryChanges)
            self.CitationStyleLastDelimiterText.textChanged.connect(self.TemporaryChanges)
            self.CitationStyleSaveButton.clicked.connect(self.SaveCitationStyle)

            for model in models:
                self.CitationStyleModelChoose.addItem(model)
                self.CitationStyleModelOrder.append(model)

            #self.CitationModelChangeHandler()

            self.NewStyleWindowLayout.addWidget(self.CitationStyleName, 0, 0, 1, 2)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleModelChoose, 1, 0)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleTypeChoose, 1, 1)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleModelFieldsChoose, 3, 0)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleAddFieldToSyntax, 3, 1)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleSyntaxBox, 4, 0, 1, 2)
            self.NewStyleWindowLayout.addWidget(self.CitationStylePreviewBox, 5, 0, 1, 2)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleMultipleDelimiterLabel, 6, 0)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleMultipleDelimiterText, 6, 1)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleLastDelimiterLabel, 7, 0)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleLastDelimiterText, 7, 1)
            self.NewStyleWindowLayout.addWidget(self.CitationStyleSaveButton, 8, 0, 1, 2)

            if edit:
                self.CitationStyleName.setDisabled(True)
                self.CitationStyleName.setText(cit.name)
                self.CitationStyleModelChoose.setDisabled(True)
                self.CitationStyleModelChoose.setCurrentIndex(self.CitationStyleModelOrder.index(cit.model.name))
                self.CitationStyleMultipleDelimiterText.setText(cit.many_sep)
                self.CitationStyleLastDelimiterText.setText(cit.last_sep)
                for x, y in cit.rules.items():
                    self.NewStyleDict["rules"][x] = y
                self.CitationStyleSyntaxBox.setPlainText(cit.rules[self.CitationStyleTypeOrder[self.CitationStyleTypeChoose.currentIndex()].name])
                print(cit.rules)

            dialog.exec_()
            self.LoadCitationStyles()
            self.RefreshEditStyleMenu()

        except Exception as e:
            print(e)

    def AddFieldToSyntax(self):
        self.CitationStyleSyntaxBox.setPlainText(self.CitationStyleSyntaxBox.toPlainText() + "{{{}}}".format(self.CitationStyleFieldOrder[self.CitationStyleModelFieldsChoose.currentIndex()].name))

    def SaveCitationStyle(self):
        try:
            self.NewStyleDict["separators"]["delimiter"] = self.CitationStyleMultipleDelimiterText.text()
            self.NewStyleDict["separators"]["last"] = self.CitationStyleLastDelimiterText.text()
        except Exception as e:
            print(e)
        with open("models/{}/styles/{}.json".format(self.CitationStyleModelChoose.currentText(), self.CitationStyleName.text()), 'w') as fp:
            json.dump(self.NewStyleDict, fp)
        self.OKdialog(translations["StyleSaved"][self.language])
        self.NewStyleWindowLayout.parent().close()

    def TemporaryChanges(self):
        self.NewStyleDict["rules"][self.CitationStyleTypeOrder[self.CitationStyleTypeChoose.currentIndex()].name] = self.CitationStyleSyntaxBox.toPlainText()
        #print(self.NewStyleDict)
        try:
            if self.col.model.name == self.CitationStyleModelChoose.currentText():
                for x, y in self.col._data.items():
                    if y["type"] == self.CitationStyleTypeOrder[self.CitationStyleTypeChoose.currentIndex()].name:
                        deepkopija = copy.deepcopy(y)
                        for field, value in deepkopija.items():
                            if type(value) is list and value:
                                if len(value) > 1:
                                    deepkopija[field] = "{}{}{}".format(self.CitationStyleMultipleDelimiterText.text().join(str(x) for x in value[0:-1]), self.CitationStyleLastDelimiterText.text(), value[-1])
                                else:
                                    deepkopija[field] = value[0]
                        self.CitationStylePreviewBox.setText(self.CitationStyleSyntaxBox.toPlainText().format(**deepkopija))
            self.CitationStyleSyntaxBox.setStyleSheet("color:{};".format(self.foreground_color))
            self.CitationStylePreviewBox.setStyleSheet("color:{};".format(self.foreground_color))
        except Exception as e:
            self.CitationStylePreviewBox.setText(translations["NewCitationStylePreviewError"][self.language])
            self.CitationStyleSyntaxBox.setStyleSheet("color:{};".format(self.accent_color))
            self.CitationStylePreviewBox.setStyleSheet("color:{};".format(self.warning_color))

    def CitationTypeChangeHandler(self):
        try:
            if self.CitationStyleTypeOrder:
                if self.CitationStyleTypeOrder[self.CitationStyleTypeChoose.currentIndex()].name not in self.NewStyleDict["rules"].keys():
                    self.CitationStyleSyntaxBox.clear()
                else:
                    self.CitationStyleSyntaxBox.setPlainText(self.NewStyleDict["rules"][self.CitationStyleTypeOrder[self.CitationStyleTypeChoose.currentIndex()].name])
        except Exception as e:
            print(e)

    def CitationModelChangeHandler(self):
        self.CitationStyleTypeChoose.clear()
        self.CitationStyleModelFieldsChoose.clear()
        self.CitationStyleTypeOrder = []
        self.CitationStyleFieldOrder = []
        for type, object in models[self.CitationStyleModelChoose.currentText()]["object"].types.items():
            self.CitationStyleTypeChoose.addItem(object.label)
            self.CitationStyleTypeOrder.append(object)
        for field in models[self.CitationStyleModelChoose.currentText()]["object"].fields:
            self.CitationStyleFieldOrder.append(field)
            self.CitationStyleModelFieldsChoose.addItem(field.label)
        self.NewStyleDict = {"rules": {}, "separators": {}}

    def BIBTEXWindow(self):
        self.BIBFieldsCounter = 0
        self.BIBTypesCounter = 0
        self.BIBTEX_scroll_widgets = {}
        self.BIBFieldsHandler = {}
        self.BIBTypesHandler = {}
        self.BIBFieldOrder = []
        self.BIBOneType = False

        dialog = QDialog()
        dialog.setMinimumWidth(830)
        self.BIBTEXLayout = QGridLayout()
        dialog.setLayout(self.BIBTEXLayout)
        dialog.setWindowTitle(translations["BIBTEXMapperWindow"][self.language])
        dialog.setStyleSheet(self.stylesheet_to_use)

        self.BIBModelHandler = []
        self.BIBModelCombo = QComboBox()
        default_model = models[self.set_model]["object"]
        for model_object in models.values():
            if model_object["object"] == default_model:
                self.BIBModelCombo.addItem(model_object["object"].name)
                self.BIBModelHandler.append(model_object["object"])
        for model_object in models.values():
            if model_object["object"] != default_model:
                self.BIBModelCombo.addItem(model_object["object"].name)
                self.BIBModelHandler.append(model_object["object"])
        self.BIBModelCombo.currentIndexChanged.connect(self.BIBModelChange)
        self.BIBTEXLayout.addWidget(self.BIBModelCombo, 0, 0, 1, 4)

        self.SelectedModelObject = self.BIBModelHandler[self.BIBModelCombo.currentIndex()]

        self.BIBFieldLabel = QLabel(translations["BIBFieldMappingLabel"][self.language])
        self.BIBTypeLabel = QLabel(translations["BIBTypeMappingLabel"][self.language])
        self.BIBAddField = QPushButton(translations["BIBAddField"][self.language])
        self.BIBAddField.clicked.connect(partial(self.BIBGenerateFieldHandles, []))
        self.BIBAddType = QPushButton(translations["BIBAddType"][self.language])
        self.BIBAddType.clicked.connect(partial(self.BIBGenerateTypeHandles, []))
        self.BIBTEXLayout.addWidget(self.BIBFieldLabel, 1, 0)
        self.BIBTEXLayout.addWidget(self.BIBAddField, 1, 1)
        self.BIBTEXLayout.addWidget(self.BIBTypeLabel, 1, 2)
        self.BIBTEXLayout.addWidget(self.BIBAddType, 1, 3)

        self.GenerateBIBTEXScrollWidgets(["BIBfield", "BIBtype"], 2)

        self.BIBAllToOneTypeWidget = QWidget()
        self.BIBAllToOneTypeLayout = QVBoxLayout(self)
        self.BIBAllToOneTypeLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.BIBAllToOneTypeWidget.setLayout(self.BIBAllToOneTypeLayout)
        self.BIBTEXLayout.addWidget(self.BIBAllToOneTypeWidget, 3, 0, 1, 2)

        self.BIBAllFieldToOneTypeCheckbox = QCheckBox(translations["BIBMapAllToOneType"][self.language])
        self.BIBAllFieldToOneTypeCheckbox.stateChanged.connect(self.BIBOneTypeChanged)
        self.BIBAllToOneTypeLayout.addWidget(self.BIBAllFieldToOneTypeCheckbox)

        self.BIBTypeOrder = []
        self.BIBTypeCombo = QComboBox()
        for type in self.SelectedModelObject.types.values():
            self.BIBTypeCombo.addItem(type.label)
            self.BIBTypeOrder.append(type)
        self.BIBAllToOneTypeLayout.addWidget(self.BIBTypeCombo)

        self.BIBSaveChanges = QPushButton(translations["BIBSaveChanges"][self.language])
        self.BIBSaveChanges.clicked.connect(self.BIBStoreChanges)
        self.BIBSaveChanges.setMinimumHeight(65)
        self.BIBTEXLayout.addWidget(self.BIBSaveChanges, 3, 2, 1, 2)

        self.BIBOpenMappings()

        dialog.exec_()

    def BIBStoreChanges(self):
        try:
            BIBdict = {}
            BIBdict["fields_map"] = {}
            BIBdict["type_map"] = {}
            if self.BIBOneType:
                BIBdict["one_type"] = self.BIBTypeOrder[self.BIBTypeCombo.currentIndex()].name
            else:
                BIBdict["one_type"] = ""
            for x, y in self.BIBFieldsHandler.items():
                BIBdict["fields_map"][y["textbox"].text()] = self.BIBFieldOrder[y["field"].currentIndex()].name
            for x, y in self.BIBTypesHandler.items():
                BIBdict["type_map"][y["textbox"].text()] = self.BIBTypeOrder[y["type"].currentIndex()].name
            print(BIBdict)

            with open("models/" + self.SelectedModelObject.name + "/mappers/bibtex.json", "w") as fp:
                json.dump(BIBdict, fp)

            self.BIBTEXLayout.parent().close()


        except Exception as e:
            print(e)
        # with open("models/" + self.SelectedModelObject.name + "/mappers/bibtex.json", 'w') as fp:
        #     json.dump(self.mapping_csv_dict_for_cur_model, fp)

    def BIBOneTypeChanged(self):
        if self.BIBAllFieldToOneTypeCheckbox.isChecked():
            self.BIBOneType = self.BIBTypeOrder[self.BIBTypeCombo.currentIndex()].name
        else:
            self.BIBOneType = ""
        print(self.BIBOneType)

    def BIBOpenMappings(self):
        for x, y in self.BIBFieldsHandler.items():
            for v in y.values():
                v.setParent(None)
        self.BIBFieldsHandler = {}
        for x, y in self.BIBTypesHandler.items():
            for v in y.values():
                v.setParent(None)
        self.BIBTypesHandler = {}
        try:
            with open("models/" + self.SelectedModelObject.name + "/mappers/bibtex.json", 'r') as fp:
                BIBMapDict = json.load(fp)
            fields_count = 0
            types_count = 0
            for x, y in BIBMapDict["fields_map"].items():
                self.BIBGenerateFieldHandles([x, y])
            for x, y in BIBMapDict["type_map"].items():
                self.BIBGenerateTypeHandles([x, y])
            if BIBMapDict["one_type"]:
                self.BIBAllFieldToOneTypeCheckbox.setChecked(True)
                self.BIBOneType = self.BIBTypeOrder[self.BIBTypeCombo.currentIndex()].name
            else:
                self.BIBAllFieldToOneTypeCheckbox.setChecked(False)
                self.BIBOneType = ""
        except Exception as e:
            print(e)

    def BIBModelChange(self):
        self.SelectedModelObject = self.BIBModelHandler[self.BIBModelCombo.currentIndex()]
        for x in self.BIBTypeOrder:
            self.BIBTypeCombo.removeItem(self.BIBTypeOrder.index(x))
        self.BIBTypeOrder = []
        for type in self.SelectedModelObject.types.values():
            self.BIBTypeCombo.addItem(type.label)
            self.BIBTypeOrder.append(type)
        self.BIBOpenMappings()

    def BIBGenerateFieldHandles(self, filler):
        textbox = QLineEdit()
        textbox.setPlaceholderText(translations["BIBField"][self.language])
        modelfieldscombo = QComboBox()
        for field in self.SelectedModelObject.fields:
            if field.name != "id":
                modelfieldscombo.addItem(field.label)
                self.BIBFieldOrder.append(field)
        remove = QPushButton(translations["BIBRemoveButton"][self.language])
        remove.clicked.connect(partial(self.BIBRemoveFieldObjects, self.BIBFieldsCounter))

        if filler:
            textbox.setText(filler[0])
            for field in self.BIBFieldOrder:
                if field.name == filler[1]:
                    modelfieldscombo.setCurrentIndex(self.BIBFieldOrder.index(field))

        self.BIBTEX_scroll_widgets["BIBfield"].addWidget(textbox, self.BIBFieldsCounter, 0)
        self.BIBTEX_scroll_widgets["BIBfield"].addWidget(modelfieldscombo, self.BIBFieldsCounter, 1)
        self.BIBTEX_scroll_widgets["BIBfield"].addWidget(remove, self.BIBFieldsCounter, 2)

        self.BIBFieldsHandler[self.BIBFieldsCounter] = {"textbox": textbox, "field": modelfieldscombo, "remove": remove}

        self.BIBFieldsCounter += 1

    def BIBRemoveFieldObjects(self, count):
        for y in self.BIBFieldsHandler[count].values():
            y.setParent(None)
        del self.BIBFieldsHandler[count]

    def BIBRemoveTypeObjects(self, count):
        for y in self.BIBTypesHandler[count].values():
            y.setParent(None)
        del self.BIBTypesHandler[count]

    def BIBGenerateTypeHandles(self, filler):
        textbox = QLineEdit()
        textbox.setPlaceholderText(translations["BIBType"][self.language])
        modeltypecombo = QComboBox()
        for type_object in self.SelectedModelObject.types.values():
            modeltypecombo.addItem(type_object.label)
            self.BIBTypeOrder.append(type_object)
        remove = QPushButton(translations["BIBRemoveButton"][self.language])
        remove.clicked.connect(partial(self.BIBRemoveTypeObjects, self.BIBTypesCounter))

        self.BIBTEX_scroll_widgets["BIBtype"].addWidget(textbox, self.BIBTypesCounter, 0)
        self.BIBTEX_scroll_widgets["BIBtype"].addWidget(modeltypecombo, self.BIBTypesCounter, 1)
        self.BIBTEX_scroll_widgets["BIBtype"].addWidget(remove, self.BIBTypesCounter, 2)

        if filler:
            textbox.setText(filler[0])
            for type in self.BIBTypeOrder:
                if type.name == filler[1]:
                    modeltypecombo.setCurrentIndex(self.BIBTypeOrder.index(type))

        self.BIBTypesHandler[self.BIBTypesCounter] = {"textbox": textbox, "type": modeltypecombo, "remove": remove}

        self.BIBTypesCounter += 1


    def GenerateBIBTEXScrollWidgets(self, names, position):
        i = 0
        for name in names:
            csv_scroll_widget = QWidget()
            scroll_layout = QGridLayout(self)
            scroll_layout.setAlignment(QtCore.Qt.AlignTop)
            csv_scroll_widget.setLayout(scroll_layout)
            scroller = QScrollArea()
            scroller.setWidgetResizable(True)
            scroller.setFrameStyle(QFrame.StyledPanel)
            scroller.setWidget(csv_scroll_widget)
            scroller.setMinimumHeight(300)
            scroller.setMinimumWidth(400)
            self.BIBTEXLayout.addWidget(scroller, position, i, 1, 2)
            self.BIBTEX_scroll_widgets[name] = scroll_layout
            i += 2

    def PrepareItemsWindow(self):
        dialog = QDialog()
        self.PrepareItemsLayout = QGridLayout()
        dialog.setLayout(self.PrepareItemsLayout)
        dialog.setWindowTitle(translations["PrepareItemsWindowTitle"][self.language])
        dialog.setStyleSheet(self.stylesheet_to_use)

        self.ApplyToAll = True
        self.PrepReports = True
        self.PrepareItemsWidth = 600

        self.AvailableFields = []
        for field in self.model_in_use.fields:
            if field.name != "id" and field.name != "type":
                self.AvailableFields.append(field)
        self.InversionFunctionLabel = QLabel(translations["InversionFunctionLabel"][self.language])
        self.PrepareItemsLayout.addWidget(self.InversionFunctionLabel, 2, 0)
        self.InversionFunctionWidget = QWidget()
        self.InversionFunctionWidget.setMinimumWidth(self.PrepareItemsWidth)
        self.InversionFunctionLayout = QHBoxLayout(self)
        self.InversionFunctionLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.InversionFunctionWidget.setLayout(self.InversionFunctionLayout)
        self.PrepareItemsLayout.addWidget(self.InversionFunctionWidget, 2, 1)
        self.InverseByTextbox = QLineEdit()
        self.InverseByTextbox.setPlaceholderText(translations["InversionFunctionInverseByPlaceholder"][self.language])
        self.InverseByField = QComboBox()
        for field in self.AvailableFields:
            self.InverseByField.addItem(field.label)
        self.InverseByExecute = QPushButton(translations["ExecuteButton"][self.language])
        self.InverseByExecute.clicked.connect(self.InverseHandler)
        self.InversionFunctionLayout.addWidget(self.InverseByTextbox)
        self.InversionFunctionLayout.addWidget(self.InverseByField)
        self.InversionFunctionLayout.addWidget(self.InverseByExecute)

        self.SplitFunctionLabel = QLabel(translations["SplitFunctionLabel"][self.language])
        self.PrepareItemsLayout.addWidget(self.SplitFunctionLabel, 3, 0)
        self.SplitFunctionWidget = QWidget()
        self.SplitFunctionWidget.setMinimumWidth(self.PrepareItemsWidth)
        self.SplitFunctionLayout = QHBoxLayout(self)
        self.SplitFunctionLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.SplitFunctionWidget.setLayout(self.SplitFunctionLayout)
        self.PrepareItemsLayout.addWidget(self.SplitFunctionWidget, 3, 1)
        self.SplitByTextbox = QLineEdit()
        self.SplitByTextbox.setPlaceholderText(translations["SplitByTextPlaceholder"][self.language])
        self.SplitByField = QComboBox()
        for field in self.AvailableFields:
            self.SplitByField.addItem(field.label)
        self.SplitByExecute = QPushButton(translations["ExecuteButton"][self.language])
        self.SplitByExecute.clicked.connect(self.SplitHandler)
        self.SplitFunctionLayout.addWidget(self.SplitByTextbox)
        self.SplitFunctionLayout.addWidget(self.SplitByField)
        self.SplitFunctionLayout.addWidget(self.SplitByExecute)


        toto = QFrame()
        toto.setFrameShape(QFrame.HLine)
        toto.setFrameShadow(QFrame.Sunken)

        self.PrepareItemsLayout.addWidget(toto, 1, 0, 1, 2)

        self.ReportOnChanges = QCheckBox(translations["PrepareItemsWindowDoReport"][self.language])
        self.ReportOnChanges.stateChanged.connect(self.ReportStateChange)
        self.ReportOnChanges.setChecked(True)
        # self.ChangesReportWidget = QWidget()
        # self.ChangesReportWidget.setMinimumWidth(400)
        # self.ChangesReportLayout = QHBoxLayout(self)
        # self.ChangesReportLayout.setAlignment(QtCore.Qt.AlignLeft)
        # self.ChangesReportWidget.setLayout(self.ChangesReportLayout)
        # self.PrepareItemsLayout.addWidget(self.ChangesReportWidget, 11, 0, 1, 2)
        # self.ChangesReportLayout.addWidget(self.ReportOnChanges)



        self.RadioApplyToAll = QRadioButton(translations["ApplyToAllItems"][self.language])
        self.RadioApplyToAll.setChecked(True)
        self.RadioApplyToAll.toggled.connect(self.ApplyToChanged)
        self.RadioApplyToSelected = QRadioButton(translations["ApplyToSelectedItems"][self.language])
        self.RadiosWidget = QWidget()
        self.RadiosWidget.setMinimumWidth(self.PrepareItemsWidth)
        self.RadiosLayout = QHBoxLayout(self)
        self.RadiosLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.RadiosWidget.setLayout(self.RadiosLayout)
        self.PrepareItemsLayout.addWidget(self.RadiosWidget, 0, 0, 1, 2)
        self.RadiosLayout.addWidget(self.RadioApplyToAll)
        self.RadiosLayout.addWidget(self.RadioApplyToSelected)
        self.RadiosLayout.addWidget(self.ReportOnChanges)



        self.ReplaceFunctionLabel = QLabel(translations["ReplaceFromItemLabel"][self.language])
        self.PrepareItemsLayout.addWidget(self.ReplaceFunctionLabel, 4, 0)
        self.ReplaceFunctionWidget = QWidget()
        self.ReplaceFunctionWidget.setMinimumWidth(self.PrepareItemsWidth)
        self.ReplaceFunctionLayout = QHBoxLayout(self)
        self.ReplaceFunctionLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.ReplaceFunctionWidget.setLayout(self.ReplaceFunctionLayout)
        self.PrepareItemsLayout.addWidget(self.ReplaceFunctionWidget, 4, 1)
        self.ReplaceByTextbox = QLineEdit()
        self.ReplaceByTextbox.setPlaceholderText(translations["ReplaceFromItemPlaceholder"][self.language])
        self.ReplaceWithTextbox = QLineEdit()
        self.ReplaceWithTextbox.setPlaceholderText(translations["ReplaceWith"][self.language])
        self.ReplaceByField = QComboBox()
        for field in self.AvailableFields:
            self.ReplaceByField.addItem(field.label)
        self.ReplaceByExecute = QPushButton(translations["ExecuteButton"][self.language])
        self.ReplaceByExecute.clicked.connect(self.ReplaceHandler)
        self.ReplaceFunctionLayout.addWidget(self.ReplaceByTextbox)
        self.ReplaceFunctionLayout.addWidget(self.ReplaceWithTextbox)
        self.ReplaceFunctionLayout.addWidget(self.ReplaceByField)
        self.ReplaceFunctionLayout.addWidget(self.ReplaceByExecute)

        self.CaseFunctionLabel = QLabel(translations["CaseFunctionLabel"][self.language])
        self.PrepareItemsLayout.addWidget(self.CaseFunctionLabel, 5, 0)
        self.CaseFunctionWidget = QWidget()
        self.CaseFunctionWidget.setMinimumWidth(self.PrepareItemsWidth)
        self.CaseFunctionLayout = QGridLayout(self)
        #self.CaseFunctionLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.CaseFunctionWidget.setLayout(self.CaseFunctionLayout)
        self.PrepareItemsLayout.addWidget(self.CaseFunctionWidget, 5, 1)
        self.CaseCombo = QComboBox()
        self.forcases = ["CaseSentence", "CaseTitle", "CaseLower", "CaseUpper"]
        for case in self.forcases:
            self.CaseCombo.addItem(translations[case][self.language])
        self.CaseFields = QComboBox()
        for field in self.AvailableFields:
            self.CaseFields.addItem(field.label)
        self.CaseExecute = QPushButton(translations["ExecuteButton"][self.language])
        self.CaseExecute.clicked.connect(self.CaseHandler)
        self.CaseFunctionLayout.addWidget(self.CaseCombo, 0, 0)
        self.CaseFunctionLayout.addWidget(self.CaseFields, 0, 1)
        self.CaseFunctionLayout.addWidget(self.CaseExecute, 0, 2)

        self.SubstringFunctionLabel = QLabel(translations["SubstringFunctionLabel"][self.language])
        self.PrepareItemsLayout.addWidget(self.SubstringFunctionLabel, 6, 0)
        self.SubstringFunctionWidget = QWidget()
        self.SubstringFunctionWidget.setMinimumWidth(self.PrepareItemsWidth)
        self.SubstringFunctionLayout = QGridLayout(self)
        self.SubstringFunctionWidget.setLayout(self.SubstringFunctionLayout)
        self.PrepareItemsLayout.addWidget(self.SubstringFunctionWidget, 6, 1)
        self.SubstringFields = QComboBox()
        for field in self.AvailableFields:
            self.SubstringFields.addItem(field.label)
        self.SubstringFirst = QLineEdit()
        self.SubstringDelim = QLabel(":")
        self.SubstringLast = QLineEdit()
        self.SubstringExecute = QPushButton(translations["ExecuteButton"][self.language])
        self.SubstringExecute.clicked.connect(self.SubstringHandler)
        self.SubstringFunctionLayout.addWidget(self.SubstringFields, 0, 0)
        self.SubstringFunctionLayout.addWidget(self.SubstringFirst, 0, 1)
        self.SubstringFunctionLayout.addWidget(self.SubstringDelim, 0, 2)
        self.SubstringFunctionLayout.addWidget(self.SubstringLast, 0, 3)
        self.SubstringFunctionLayout.addWidget(self.SubstringExecute, 0, 4)

        dialog.exec_()

    def SubstringHandler(self):
        self.FireTempSave()
        report = additional_functions.Substring(self.col, self.AvailableFields[self.SubstringFields.currentIndex()], self.SubstringFirst.text(), self.SubstringLast.text(), self.ApplyToAll)
        if self.PrepReports:
            self.ItemPrepReport(report)
        self.RefreshCollectionView()
        self.FireTempSave()

    def CaseHandler(self):
        self.FireTempSave()
        report = additional_functions.ChangeCase(self.col, self.AvailableFields[self.CaseFields.currentIndex()], self.forcases[self.CaseCombo.currentIndex()], self.ApplyToAll)
        if self.PrepReports:
            self.ItemPrepReport(report)
        self.RefreshCollectionView()
        self.FireTempSave()

    def ReplaceHandler(self):
        self.FireTempSave()
        report = additional_functions.Replace(self.col, self.AvailableFields[self.ReplaceByField.currentIndex()], self.ReplaceByTextbox.text(), self.ReplaceWithTextbox.text(), self.ApplyToAll)
        if self.PrepReports:
            self.ItemPrepReport(report)
        self.RefreshCollectionView()
        self.FireTempSave()

    def ReportStateChange(self):
        if self.ReportOnChanges.isChecked():
            self.PrepReports = True
        else:
            self.PrepReports = False

    def SplitHandler(self):
        self.FireTempSave()
        report = additional_functions.Split(self.col, self.AvailableFields[self.SplitByField.currentIndex()], self.SplitByTextbox.text(), self.ApplyToAll)
        if self.PrepReports:
            self.ItemPrepReport(report)
        self.RefreshCollectionView()
        self.FireTempSave()

    def ApplyToChanged(self):
        if self.RadioApplyToAll.isChecked():
            self.ApplyToAll = True
        else:
            self.ApplyToAll = False

    def RemoveFromItemHandler(self):
        pass

    def InverseHandler(self):
        self.FireTempSave()
        report = additional_functions.Inverse(self.col, self.AvailableFields[self.InverseByField.currentIndex()], self.InverseByTextbox.text(), self.ApplyToAll)
        if self.PrepReports:
            self.ItemPrepReport(report)
        self.RefreshCollectionView()
        self.FireTempSave()

    def ItemPrepReport(self, reportlist):
        dialog = QDialog()
        self.PrepReportLayout = QGridLayout()
        dialog.setLayout(self.PrepReportLayout)
        dialog.setWindowTitle(translations["ItemPrepReportWindowTitle"][self.language])
        dialog.setStyleSheet(self.stylesheet_to_use)

        self.ReportBox = QTextEdit()
        self.ReportBox.setReadOnly(True)
        if reportlist:
            self.ReportBox.setText("<hr>".join(reportlist))
            self.ReportBox.setMinimumHeight(500)
            self.ReportBox.setMinimumWidth(500)
        else:
            self.ReportBox.setText(translations["PrepReportNoChangesMade"][self.language])
            self.ReportBox.setAlignment(QtCore.Qt.AlignCenter)
            self.ReportBox.setMinimumHeight(100)
            self.ReportBox.setMinimumWidth(400)
        self.PrepReportLayout.addWidget(self.ReportBox, 0, 0)

        self.ReportOKButton = QPushButton(translations["OKButtonUniversal"][self.language])
        self.ReportOKButton.clicked.connect(dialog.close)
        self.PrepReportLayout.addWidget(self.ReportOKButton, 1, 0)

        dialog.exec_()

    def UNIMARCWindow(self):
        try:
            self.UNIFieldsCounter = 0
            self.UNITypesCounter = 0
            self.UNI_scroll_widgets = {}
            self.UNIFieldsHandler = {}
            self.UNITypesHandler = {}
            self.UNIFieldOrder = []
            self.UNITypeOrder = []
            self.UNIOneType = False

            dialog = QDialog()
            dialog.setMinimumWidth(830)
            self.UNIMARCLayout = QGridLayout()
            dialog.setLayout(self.UNIMARCLayout)
            dialog.setWindowTitle(translations["UNIMARCMapperWindow"][self.language])
            dialog.setStyleSheet(self.stylesheet_to_use)

            self.UNIModelHandler = []
            self.UNIModelCombo = QComboBox()
            default_model = models[self.set_model]["object"]
            for model_object in models.values():
                if model_object["object"] == default_model:
                    self.UNIModelCombo.addItem(model_object["object"].name)
                    self.UNIModelHandler.append(model_object["object"])
            for model_object in models.values():
                if model_object["object"] != default_model:
                    self.UNIModelCombo.addItem(model_object["object"].name)
                    self.UNIModelHandler.append(model_object["object"])
            self.UNIModelCombo.currentIndexChanged.connect(self.UNIModelChange)
            self.UNIMARCLayout.addWidget(self.UNIModelCombo, 0, 0, 1, 4)

            self.UNISelectedModelObject = self.UNIModelHandler[self.UNIModelCombo.currentIndex()]

            self.UNIFieldLabel = QLabel(translations["UNIMARCFieldLabel"][self.language])
            self.UNITypeLabel = QLabel(translations["UNIMARCTypeLabel"][self.language])
            self.UNIAddField = QPushButton(translations["UNIMARCAddFieldButton"][self.language])
            self.UNIAddField.clicked.connect(partial(self.UNIGenerateFieldHandles, []))
            self.UNIAddType = QPushButton(translations["UNIMARCAddTypeButton"][self.language])
            self.UNIAddType.clicked.connect(partial(self.UNIGenerateTypeHandles, []))
            self.UNIMARCLayout.addWidget(self.UNIFieldLabel, 1, 0)
            self.UNIMARCLayout.addWidget(self.UNIAddField, 1, 1)
            self.UNIMARCLayout.addWidget(self.UNITypeLabel, 1, 2)
            self.UNIMARCLayout.addWidget(self.UNIAddType, 1, 3)

            self.GenerateUNIMARCScollWidgets(["UNIfield", "UNItype"], 2)

            self.UNIAllToOneTypeWidget = QWidget()
            self.UNIAllToOneTypeLayout = QVBoxLayout(self)
            self.UNIAllToOneTypeLayout.setAlignment(QtCore.Qt.AlignLeft)
            self.UNIAllToOneTypeWidget.setLayout(self.UNIAllToOneTypeLayout)
            self.UNIMARCLayout.addWidget(self.UNIAllToOneTypeWidget, 3, 0, 1, 2)

            self.UNIMARCFieldToOneTypeCheckbox = QCheckBox(translations["UNIMARCOneTypeCheckbox"][self.language])
            self.UNIMARCFieldToOneTypeCheckbox.stateChanged.connect(self.UNIOneTypeChanged)
            self.UNIAllToOneTypeLayout.addWidget(self.UNIMARCFieldToOneTypeCheckbox)

            self.UNITypeCombo = QComboBox()
            for type in self.UNISelectedModelObject.types.values():
                self.UNITypeCombo.addItem(type.label)
                self.UNITypeOrder.append(type)
            self.UNIAllToOneTypeLayout.addWidget(self.UNITypeCombo)

            self.UNISaveChanges = QPushButton(translations["UNIMARCSaveChangesButton"][self.language])
            self.UNISaveChanges.clicked.connect(self.UNIStoreChanges)
            self.UNISaveChanges.setMinimumHeight(65)
            self.UNIMARCLayout.addWidget(self.UNISaveChanges, 3, 2, 1, 2)

            self.UNIOpenMappings()

            dialog.exec_()
        except Exception as e:
            print(e)

    def UNIModelChange(self):
        self.UNISelectedModelObject = self.UNIModelHandler[self.UNIModelCombo.currentIndex()]
        for x in self.UNITypeOrder:
            self.UNITypeCombo.removeItem(self.UNITypeOrder.index(x))
        self.UNITypeOrder = []
        for type in self.UNISelectedModelObject.types.values():
            self.UNITypeCombo.addItem(type.label)
            self.UNITypeOrder.append(type)
        self.UNIOpenMappings()

    def UNIGenerateFieldHandles(self, filler):
        textbox = QLineEdit()
        textbox.setPlaceholderText(translations["UNIMARCField"][self.language])
        modelfieldscombo = QComboBox()
        for field in self.UNISelectedModelObject.fields:
            if field.name != "id":
                modelfieldscombo.addItem(field.label)
                self.UNIFieldOrder.append(field)
        remove = QPushButton(translations["UNIMARCRemove"][self.language])
        remove.clicked.connect(partial(self.UNIRemoveFieldObjects, self.UNIFieldsCounter))

        if filler:
            textbox.setText(filler[0])
            for field in self.UNIFieldOrder:
                if field.name == filler[1]:
                    modelfieldscombo.setCurrentIndex(self.UNIFieldOrder.index(field))

        self.UNI_scroll_widgets["UNIfield"].addWidget(textbox, self.UNIFieldsCounter, 0)
        self.UNI_scroll_widgets["UNIfield"].addWidget(modelfieldscombo, self.UNIFieldsCounter, 1)
        self.UNI_scroll_widgets["UNIfield"].addWidget(remove, self.UNIFieldsCounter, 2)

        self.UNIFieldsHandler[self.UNIFieldsCounter] = {"textbox": textbox, "field": modelfieldscombo, "remove": remove}

        self.UNIFieldsCounter += 1

    def UNIRemoveFieldObjects(self, count):
        for y in self.UNIFieldsHandler[count].values():
            y.setParent(None)
        del self.UNIFieldsHandler[count]

    def UNIRemoveTypeObjects(self, count):
        for y in self.UNITypesHandler[count].values():
            y.setParent(None)
        del self.UNITypesHandler[count]

    def UNIGenerateTypeHandles(self, filler):
        textbox = QLineEdit()
        textbox.setPlaceholderText(translations["UNIMARCTypePlaceholder"][self.language])
        modeltypecombo = QComboBox()
        for type_object in self.UNISelectedModelObject.types.values():
            modeltypecombo.addItem(type_object.label)
            self.UNITypeOrder.append(type_object)
        remove = QPushButton(translations["UNIMARCRemove"][self.language])
        remove.clicked.connect(partial(self.UNIRemoveTypeObjects, self.UNITypesCounter))

        self.UNI_scroll_widgets["UNItype"].addWidget(textbox, self.UNITypesCounter, 0)
        self.UNI_scroll_widgets["UNItype"].addWidget(modeltypecombo, self.UNITypesCounter, 1)
        self.UNI_scroll_widgets["UNItype"].addWidget(remove, self.UNITypesCounter, 2)

        if filler:
            textbox.setText(filler[0])
            for type in self.UNITypeOrder:
                if type.name == filler[1]:
                    modeltypecombo.setCurrentIndex(self.UNITypeOrder.index(type))

        self.UNITypesHandler[self.UNITypesCounter] = {"textbox": textbox, "type": modeltypecombo, "remove": remove}

        self.UNITypesCounter += 1

    def GenerateUNIMARCScollWidgets(self, names, position):
        i = 0
        for name in names:
            uni_scroll_widget = QWidget()
            scroll_layout = QGridLayout(self)
            scroll_layout.setAlignment(QtCore.Qt.AlignTop)
            uni_scroll_widget.setLayout(scroll_layout)
            scroller = QScrollArea()
            scroller.setWidgetResizable(True)
            scroller.setFrameStyle(QFrame.StyledPanel)
            scroller.setWidget(uni_scroll_widget)
            scroller.setMinimumHeight(300)
            scroller.setMinimumWidth(400)
            self.UNIMARCLayout.addWidget(scroller, position, i, 1, 2)
            self.UNI_scroll_widgets[name] = scroll_layout
            i += 2

    def UNIOneTypeChanged(self):
        if self.UNIMARCFieldToOneTypeCheckbox.isChecked():
            self.UNIOneType = self.UNITypeOrder[self.UNITypeCombo.currentIndex()].name
        else:
            self.UNIOneType = ""

    def UNIStoreChanges(self):
        UNIdict = {}
        UNIdict["fields_map"] = {}
        UNIdict["type_map"] = {}
        if self.UNIOneType:
            UNIdict["one_type"] = self.UNITypeOrder[self.UNITypeCombo.currentIndex()].name
        else:
            UNIdict["one_type"] = ""
        for x, y in self.UNIFieldsHandler.items():
            UNIdict["fields_map"][y["textbox"].text()] = self.UNIFieldOrder[y["field"].currentIndex()].name
        for x, y in self.UNITypesHandler.items():
            UNIdict["type_map"][y["textbox"].text()] = self.UNITypeOrder[y["type"].currentIndex()].name

        with open("models/"+self.UNISelectedModelObject.name + "/mappers/unimarc.json", "w") as fp:
            json.dump(UNIdict, fp)

        self.UNIMARCLayout.parent().close()

    def UNIOpenMappings(self):
        self.UNIFieldsCounter = 0
        self.UNITypesCounter = 0
        self.UNIFieldsHandler = {}
        self.UNITypesHandler = {}
        self.UNIFieldOrder = []
        self.UNITypeOrder = []
        self.UNIOneType = False
        file = "models/"+self.UNISelectedModelObject.name+"/mappers/unimarc.json"
        for i in reversed(range(self.UNI_scroll_widgets["UNItype"].count())):
            self.UNI_scroll_widgets["UNItype"].itemAt(i).widget().setParent(None)
        for i in reversed(range(self.UNI_scroll_widgets["UNIfield"].count())):
            self.UNI_scroll_widgets["UNIfield"].itemAt(i).widget().setParent(None)
        if os.path.isfile(file):
            with open(file, "r") as fp:
                UNIMapDict = json.load(fp)
            fields_count = 0
            types_count = 0
            for x, y in UNIMapDict["fields_map"].items():
                self.UNIGenerateFieldHandles([x, y])
            for x, y in UNIMapDict["type_map"].items():
                self.UNIGenerateTypeHandles([x, y])
            if UNIMapDict["one_type"]:
                self.UNIMARCFieldToOneTypeCheckbox.setChecked(True)
                self.UNIOneType = self.UNITypeOrder[self.UNITypeCombo.currentIndex()].name
            else:
                self.UNIMARCFieldToOneTypeCheckbox.setChecked(False)


    def PermaSaveWindow(self):
        no_collection = False
        try:
            print(self.col._data)
        except Exception as e:
            no_collection = True
        if no_collection:
            self.OKdialog(translations["NoCollection"][self.language])
        else:
            dialog = QDialog()
            dialog.setMinimumWidth(500)
            self.PermaSaveLayout = QGridLayout()
            dialog.setLayout(self.PermaSaveLayout)
            dialog.setWindowTitle(translations["PermaSaveCollectionWindowTitle"][self.language])
            dialog.setStyleSheet(self.stylesheet_to_use)

            self.PermaSaveName = QLineEdit()
            self.PermaSaveName.setPlaceholderText(translations["PermaSaveNamePlaceholder"][self.language])
            self.PermaSaveLayout.addWidget(self.PermaSaveName, 0, 0, 1, 2)

            self.OverwriteCheck = QCheckBox(translations["PermaOverwriteBox"][self.language])
            self.PermaSaveLayout.addWidget(self.OverwriteCheck, 1, 0, 1, 1)

            self.ExistsWarning = QLabel(translations["PermaSaveExistsWarning"][self.language])
            self.ExistsWarning.setStyleSheet("color:"+self.warning_color+";")
            self.ExistsWarning.setVisible(False)
            self.PermaSaveLayout.addWidget(self.ExistsWarning, 2, 0, 1, 1)

            self.PermaSaveButton = QPushButton(translations["PermaSaveButton"][self.language])
            self.PermaSaveButton.clicked.connect(self.PermaSaveExecute)
            self.PermaSaveLayout.addWidget(self.PermaSaveButton, 1, 1, 1, 1)

            dialog.exec_()

    def PermaSaveExecute(self):
        collection_name = self.PermaSaveName.text()
        my_file = "saves/" + collection_name
        exists = os.path.isfile(my_file)
        if exists and not self.OverwriteCheck.isChecked():
            self.ExistsWarning.setVisible(True)
        else:
            self.col.PermaSave(collection_name)
            time_saved = datetime.datetime.now()
            time_saved_adjusted = time_saved.strftime("%d.%m.%Y %H:%M:%S")
            self.collections[collection_name] = {"model": self.col.model.name, "items_count": len(self.col._data), "bin_count": len(self.col._recyclebin), "selected_count": len(self.col._selected_items), "time": time_saved_adjusted}
            self.SaveCollectionMetadata()
            self.OKdialog(translations["CollectionPermaSaved"][self.language])
            self.PermaSaveLayout.parent().close()

    def OpenSavedCollectionsMetadata(self):
        with open("saved_collections.json") as json_data:
            self.collections = json.load(json_data)

    def SaveCollectionMetadata(self):
        with open("saved_collections.json", 'w') as fp:
            json.dump(self.collections, fp)

    def OpenCollectionWindow(self):
        self.OpenColObjectsHandler = {}
        dialog = QDialog()
        dialog.setMinimumWidth(500)
        self.OpenColLayout = QGridLayout()
        dialog.setLayout(self.OpenColLayout)
        dialog.setWindowTitle(translations["OpenExistingCollectionWindow"][self.language])
        dialog.setStyleSheet(self.stylesheet_to_use + "* {margin-right:15px;}")

        print(self.collections)

        label_headers = [translations["OpenColColName"][self.language],translations["OpenColModel"][self.language],translations["OpenColItemsCount"][self.language], translations["OpenColTime"][self.language]]

        i = 0
        for label in label_headers:
            new_label = QLabel(label)
            new_label.setStyleSheet("color:{};".format(self.accent_color))
            if label == translations["OpenColColName"][self.language]:
                self.OpenColLayout.addWidget(new_label, 0, i, 1, 3)
                i += 3
            else:
                self.OpenColLayout.addWidget(new_label, 0, i)
                i += 1

        p = 1
        for x, y in self.collections.items():
            col_name_label = QLabel("<b>"+x+"</b>")
            self.OpenColLayout.addWidget(col_name_label, p, 0)

            open_col_button = QPushButton(translations["OpenColButton"][self.language])
            open_col_button.setMinimumWidth(100)
            open_col_button.clicked.connect(partial(self.LoadCollection, x, y["model"], dialog))
            self.OpenColLayout.addWidget(open_col_button, p, 1)

            remove_col_button = QPushButton(translations["RemoveColButton"][self.language])
            remove_col_button.setMinimumWidth(100)
            remove_col_button.setStyleSheet("background-color:{};".format(self.warning_color))
            remove_col_button.clicked.connect(partial(self.RemoveCollection, x))
            self.OpenColLayout.addWidget(remove_col_button, p, 2)

            col_model_label = QLabel(y["model"])
            self.OpenColLayout.addWidget(col_model_label, p, 3)
            col_item_count_label = QLabel(str(y["items_count"]))
            self.OpenColLayout.addWidget(col_item_count_label, p, 4)
            col_time = QLabel(y["time"])
            self.OpenColLayout.addWidget(col_time, p, 5)

            self.OpenColObjectsHandler[x] = [col_name_label, open_col_button, remove_col_button, col_model_label, col_item_count_label, col_time]

            p+=1


        dialog.exec_()

    def RemoveCollection(self, collection_name):
        for each in self.OpenColObjectsHandler[collection_name]:
            each.setParent(None)
        del self.collections[collection_name]
        self.SaveCollectionMetadata()
        os.remove("saves/{}".format(collection_name))


    def LoadCollection(self, collection, model, sender):
        self.NewCollection(model)
        with open("saves/"+collection) as json_data:
            loaded_collection = json.load(json_data)
        #self.col._data = loaded_collection["data"]

        for x, y in loaded_collection["data"].items():
           self.col._data[int(x)] = y

        #self.col._recyclebin = loaded_collection["bin"]

        for x, y in loaded_collection["bin"].items():
            self.col._recyclebin[int(x)] = y
        self.col._current_id = loaded_collection["current_id"]
        self.col._grouping_index = loaded_collection["grouping"]
        self.col._filtering_index = loaded_collection["filtering"]
        self.col._selected_items = loaded_collection["selected"]
        self.col._view_field = loaded_collection["view_field"]

        self.import_reporter_handler = []
        for x, y in self.col._data.items():
            y["jednostavni_godina"] = int(y["jednostavni_godina"])
        for item in self.col._data.values():
            empty, invalid, faultyitem = self.col.validateItem(item)
            if empty or invalid:
                self.import_reporter_handler.append([empty, invalid, faultyitem])

        for item in self.col._recyclebin.values():
            empty, invalid, faultyitem = self.col.validateItem(item)
            if empty or invalid:
                self.import_reporter_handler.append([empty, invalid, faultyitem])

        # for key, value in self.col._data.items():
        #     self.col._data[int(value["id"])] = self.col._data.pop(key)

        for key, value in self.col._data.items():
            if type(key) != int:
                raise Exception("AJME", type(key), key, type(value["id"]), value["id"])

        if self.import_reporter_handler:
            self.ImportErrorReportWindow()

        self.RefreshCollectionView()

        sender.close()

    def APAStyleWindow(self):
        dialog = QDialog()
        dialog.setMinimumWidth(800)
        self.APALayout = QGridLayout()
        dialog.setLayout(self.APALayout)
        dialog.setWindowTitle(translations["APACitationStyleWindow"][self.language])
        dialog.setStyleSheet(self.stylesheet_to_use)

        self.APAPanesDict = {}

        self.APAModelChoose = QComboBox()
        self.APAFieldLabel = QLabel(translations["APAFieldLabel"][self.language])
        self.APATypeLabel = QLabel(translations["APATypeLabel"][self.language])
        self.APAAddFieldButton = QPushButton(translations["APAAddField"][self.language])
        self.APAAddTypeButton = QPushButton(translations["APAAddType"][self.language])
        self.APASaveChanges = QPushButton(translations["APASaveChanges"][self.language])
        self.APASaveChanges.setMinimumHeight(50)
        self.APASaveChanges.clicked.connect(self.SaveAPAMapping)

        self.APALayout.addWidget(self.APAModelChoose, 0, 0, 1, 4)
        self.APALayout.addWidget(self.APAFieldLabel, 1, 0)
        self.APALayout.addWidget(self.APAAddFieldButton, 1, 1)
        self.APALayout.addWidget(self.APATypeLabel, 1, 2)
        self.APALayout.addWidget(self.APAAddTypeButton, 1, 3)
        self.APALayout.addWidget(self.APASaveChanges, 3, 2, 1, 2)

        self.APAAddFieldButton.clicked.connect(partial(self.AddHandle, "field"))
        self.APAAddTypeButton.clicked.connect(partial(self.AddHandle, "type"))

        self.GenerateAPAPanes(["fields", "types"])

        with open('citation_styles/APA/style.json', 'r') as fp:
            self.APA_dict = json.load(fp)

        for model in models:
            if model == self.set_model:
                self.APAModelChoose.addItem(model)

        for model in models:
            if model != self.set_model:
                self.APAModelChoose.addItem(model)

        self.HandleCounters = {"field": 0, "type": 0}
        self.HandleOrders = {"field": [], "type": []}
        self.APAHandler = {"fields": {}, "types": {}}

        self.LoadAPAMappings()

        dialog.exec_()

    def LoadAPAMappings(self):
        with open("models/{}/cit_mappers/APA.json".format(self.APAModelChoose.currentText()), 'r') as fp:
            mapper = json.load(fp)
        print(mapper)
        for x, y in mapper["type_maps"].items():
            self.AddHandle("type")
        for x, y in mapper["field_maps"].items():
            self.AddHandle("field")
        self.FillAPAHandles(mapper)

    def FillAPAHandles(self, mapdict):
        try:
            i = 0
            for x, y in mapdict["type_maps"].items():
                for type_object in self.HandleOrders["type"]:
                    if type_object.name == y:
                        self.APAHandler["types"][i][1].setCurrentIndex(self.HandleOrders["type"].index(type_object))
                self.APAHandler["types"][i][0].setCurrentIndex(self.APAHandler["types"][i][0].findText(x))
                i+=1

            i = 0
            for x, y in mapdict["field_maps"].items():
                for field_object in self.HandleOrders["field"]:
                    if field_object.name == y:
                        self.APAHandler["fields"][i][1].setCurrentIndex(self.HandleOrders["field"].index(field_object))
                self.APAHandler["fields"][i][0].setCurrentIndex(self.APAHandler["fields"][i][0].findText(x))
                i += 1
        except Exception as e:
            print(e)

    def SaveAPAMapping(self):
        try:
            dict_to_save = {"field_maps": {}, "type_maps": {}}
            for x, y in self.APAHandler["fields"].items():
                dict_to_save["field_maps"][y[0].currentText()] = self.HandleOrders["field"][y[1].currentIndex()].name
            for a, b in self.APAHandler["types"].items():
                dict_to_save["type_maps"][b[0].currentText()] = self.HandleOrders["type"][b[1].currentIndex()].name
            print(dict_to_save)
            with open("models/{}/cit_mappers/APA.json".format(self.APAModelChoose.currentText()), 'w') as fp:
                json.dump(dict_to_save, fp)
            self.APALayout.parent().close()
        except Exception as e:
            print(e)

    def AddToPane(self, objects, pane, counter):
        i = 0
        self.APAHandler[pane][self.HandleCounters[counter]] = objects
        for object in objects:
            self.APAPanesDict[pane].addWidget(object, self.HandleCounters[counter], i)
            i += 1
        self.HandleCounters[counter] += 1

    def AddHandle(self, handle_type):
        try:
            if handle_type == "field":
                apa_combo = QComboBox()
                for apa_field in self.APA_dict["Fields"].keys():
                    apa_combo.addItem(apa_field)
                field_combo = QComboBox()
                for x, y in models.items():
                    if x == self.APAModelChoose.currentText():
                        for field in y["object"].fields:
                            if field.name != "id":
                                field_combo.addItem(field.label)
                                if field not in self.HandleOrders["field"]:
                                    self.HandleOrders["field"].append(field)
                remove_button = QPushButton(translations["APARemove"][self.language])
                self.AddToPane([apa_combo, field_combo, remove_button], "fields", "field")

            elif handle_type == "type":
                apa_combo = QComboBox()
                for apa_type in self.APA_dict["Types"].keys():
                    apa_combo.addItem(apa_type)
                type_combo = QComboBox()
                for x, y in models.items():
                    if x == self.APAModelChoose.currentText():
                        for type, object in y["object"].types.items():
                            type_combo.addItem(type)
                            if object not in self.HandleOrders["type"]:
                                self.HandleOrders["type"].append(object)
                remove_button = QPushButton(translations["APARemove"][self.language])
                self.AddToPane([apa_combo, type_combo, remove_button], "types", "type")
        except Exception as e:
            print(e)

    def GenerateAPAPanes(self, names):
        i = 0
        for name in names:
            apa_scroll_widget = QWidget()
            scroll_layout = QGridLayout(self)
            scroll_layout.setAlignment(QtCore.Qt.AlignTop)
            apa_scroll_widget.setLayout(scroll_layout)
            scroller = QScrollArea()
            scroller.setWidgetResizable(True)
            scroller.setFrameStyle(QFrame.StyledPanel)
            scroller.setWidget(apa_scroll_widget)
            scroller.setMinimumHeight(300)
            scroller.setMinimumWidth(400)
            self.APALayout.addWidget(scroller, 2, i, 1, 2)
            self.APAPanesDict[name] = scroll_layout
            i += 2

    def StylesMapperHandler(self, style):
        if style == "APA":
            self.APAStyleWindow()

    def BibliographyWindow(self):
        try:
            if self.col._data:
                self.OpenBibliographyWindow()
            else:
                self.OKdialog(translations["NoItemsInCollectionWarning"][self.language])
        except:
            self.OKdialog(translations["NoCollectionWarning"][self.language])

    def OpenBibliographyWindow(self):
        dialog = QDialog()
        dialog.setMinimumWidth(800)
        self.BibliographyLayout = QGridLayout()
        dialog.setLayout(self.BibliographyLayout)
        dialog.setWindowTitle(translations["BibliographyManager"][self.language])
        dialog.setStyleSheet(self.stylesheet_to_use)

        self.BiblCitStyleCombo = QComboBox()

        for citat in self.CitationStylesList:
            self.BiblCitStyleCombo.addItem(citat.name)


        self.NumberingIndex = ["BiblNoNumbering", "BiblGlobalNumbering", "BiblLocalNumbering"]
        self.NumberingCombo = QComboBox()
        for numberstyle in self.NumberingIndex:
            self.NumberingCombo.addItem(translations[numberstyle][self.language])
        self.BiblGenerateButton = QPushButton(translations["BibliographyGenerateButton"][self.language])
        self.BiblGenerateButton.clicked.connect(self.GenerateBibliography)
        self.BiblContent = QTextEdit()
        self.BiblContent.setMinimumHeight(400)
        self.BiblExportButton = QPushButton(translations["BibliographyExportButton"][self.language])
        #self.BiblNumbering = QCheckBox(translations["BiblNumbering"][self.language])
        self.BiblExportButton.clicked.connect(self.ExportBibliographyFunc)

        self.BibliographyLayout.addWidget(self.BiblCitStyleCombo, 0, 0)
        self.BibliographyLayout.addWidget(self.NumberingCombo, 0, 1)
        self.BibliographyLayout.addWidget(self.BiblGenerateButton, 0, 2)
        self.BibliographyLayout.addWidget(self.BiblContent, 1, 0, 1, 3)
        self.BibliographyLayout.addWidget(self.BiblExportButton, 2, 2)
        #self.BibliographyLayout.addWidget(self.BiblNumbering, 2, 0)

        #print(citrules)

        self.LoadAPA()
        dialog.exec_()

    def ExportBibliographyFunc(self):
        try:
            print(self.instanced_bibliography._bibl)
            fname = QFileDialog.getSaveFileName(self, translations["SaveBibliography"][self.language], os.curdir, "PDF (*.pdf);;HTML (*.html);;TXT (*.txt)")
            if fname:
                if fname[1].startswith("PDF"):
                    self.instanced_bibliography.exportAsPDF(self.background_color, fname[0])
                elif fname[1].startswith("HTML"):
                    self.instanced_bibliography.exportAsHTML(self.background_color, fname[0])
                elif fname[1].startswith("TXT"):
                    self.instanced_bibliography.exportAsTXT(fname[0])
                if sys.platform.startswith('linux'):
                    subprocess.call(["xdg-open", fname[0]])
                else:
                    os.startfile(fname[0])
        except Exception as e:
            self.OKdialog(str(e))

    def GenerateBibliography(self):
        self.instanced_bibliography = class_bibliography.Bibliography()
        self.instanced_bibliography.generateBibliography(self.col, self.CitationStylesList[self.BiblCitStyleCombo.currentIndex()], self.NumberingCombo.currentIndex())

        html_ready = self.instanced_bibliography.prepareAsHTML(self.accent_color)
        self.BiblContent.setText(html_ready)

        # lista = self.CitationStylesList[self.BiblCitStyleCombo.currentIndex()].stylizer(self.col, self.CitationStylesList[self.BiblCitStyleCombo.currentIndex()], self.NumberingCombo.currentIndex())
        # for_bibliography = "<style>h1,h2,h3,h4,h5,h6{{color:{};}}</style>".format(self.accent_color)
        # for each in lista:
        #     for_bibliography += each
        # self.BiblContent.setText(for_bibliography)

    def LoadAPA(self):
        from citation_styles.APA.stylizer import NewAPAStylize

        with open('citation_styles/APA/style.json', 'r') as fp:
            APArules = json.load(fp)

        APAstyle = class_citation_style.CitationStyle("APA", self.col.model, APArules, many_sep=APArules["many_sep"], last_sep=APArules["last_sep"], stylizer=NewAPAStylize)

        names = []
        for style in self.CitationStylesList:
            names.append(style.name)
        if APAstyle.name not in names:
            self.CitationStylesList.append(APAstyle)

    def LoadCitationStyles(self):
        self.CitationStylesList = []
        try:
            styles_list = []
            for modelname in models:
                styles_list = os.listdir("models/{}/styles/".format(modelname))
                model_object = models[modelname]["object"]
                for style in styles_list:
                    with open('models/{}/styles/{}'.format(modelname, style), 'r') as nw:
                        style_rules = json.load(nw)
                        new_style = class_citation_style.CitationStyle(style.replace(".json", ""), model_object, style_rules["rules"], many_sep=style_rules["separators"]["delimiter"], last_sep=style_rules["separators"]["last"])
                        self.CitationStylesList.append(new_style)

                print(self.CitationStylesList)
        except Exception as e:
            print(e)

    def EditItem(self, id):
        print(id)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Azurio()
    sys.exit(app.exec_())
