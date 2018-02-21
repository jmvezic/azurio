import re

class Bibliography:
    def __init__(self):
        self._bibl = []

    def generateBibliography(self, collection, cit_style, numbering):
        stylized = cit_style.stylizer(collection, cit_style, numbering)
        self._bibl = stylized

    def prepareAsHTML(self, color):
        for_bibliography = "<style>h1,h2,h3,h4,h5,h6{{color:{};}}</style>".format(color)
        for each in self._bibl:
            for_bibliography += each
        return for_bibliography

    def exportAsPDF(self, color, path):
        html_styled = self.prepareAsHTML(color)
        import pdfkit
        path_wkthmltopdf = b'wkhtmltopdf/bin/wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        pdfkit.from_string(html_styled, path, configuration=config)

    def exportAsHTML(self, color, path):
        html_styled = self.prepareAsHTML(color)
        fo = open(path, "w")
        fo.write(html_styled)

    def cleanhtml(self, raw_html):
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", raw_html)
        return cleantext

    def exportAsTXT(self, path):
        html_data = ""
        for each in self._bibl:
            html_data += "{}\n".format(each)
        txt_ready = self.cleanhtml(html_data)
        fo = open(path, "w")
        fo.write(txt_ready)