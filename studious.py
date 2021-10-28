## studious main

import sys
# from Moore's book
from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

import ebooklib
from ebooklib import epub

import xml.etree.ElementTree as ETree
     
# Inheriting from QMainWindow broke the layouts.
class MainWindow(qtw.QMainWindow):

    SECTION = 0 # constants for the treeview
    HREF = 1
    
    def __init__(self):
        # The book doesn't pass the class and object.
        super(MainWindow, self).__init__()

        # I won't call these if I set it up myself.
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        window = qtw.QWidget()
        self.setCentralWidget(window)
        
        self.setWindowTitle("Studious Reader")
        self.resize(800,600)
        menuBar = qtw.QMenuBar(self)
        fileMenu = menuBar.addMenu("&File")
        self.setMenuBar(menuBar)
        
        topLayout = qtw.QHBoxLayout()
        window.setLayout(topLayout)
        
        leftLayout = qtw.QVBoxLayout()
        #testButton = qtw.QPushButton("Push Me", self)
        #leftLayout.addWidget(testButton)

        #self.tocPane = qtw.QTreeView(self)
        self.tocPane = qtw.QTreeWidget(self)
        self.tocPane.setColumnCount(2)
        self.tocPane.setHeaderLabels(["Section", "Link"])
        # self.tocPane.hideColumn(1)  # leaving visible for devel
        self.tocPane.itemClicked.connect(self.jump_to_tocitem)
        # self.tocModel = self.create_toc_model(self)
        # self.tocPane.setModel(self.tocModel)
        
        topLayout.addLayout(leftLayout)
        leftLayout.addWidget(self.tocPane)

        centerLayout = qtw.QVBoxLayout()
        self.mainText = qtw.QTextBrowser(self)
        self.mainText.style = """
          <style>body{ margin: 15px; line-height: 130% }</style>
        """
        mainText_font = qtg.QFont('Liberation Serif', 11)
        mainText_font.setStyleHint(qtg.QFont.Serif)
        self.mainText.setFont(mainText_font)
        self.mainText.setOpenLinks(False)
        self.mainText.anchorClicked.connect(self.jump_to_qurl)

        topLayout.addLayout(centerLayout)
        centerLayout.addWidget(self.mainText)

        self.show()

    #def create_toc_model(self, parent):
    #    model = qtg.QStandardItemModel(0, 1, parent)
    #    # can I just define constants like this?
    #    model.setHeaderData(self.SECTION, qtc.Qt.Horizontal, "Section")
    #    return model

    def jump_to(self, urlStr):
        splitUrl = urlStr.split('#')
        href = splitUrl[0]
        # sectionText = self.the_epub.get_item_with_href(href).get_content()
        # self.mainText.setHtml(sectionText.decode('utf-8'))
        if len(splitUrl) > 1:
            self.mainText.scrollToAnchor(splitUrl[1])
        else:
            print("url with no anchor...problem...")
        # TODO: move TOC highlight to wherever I jumped to
    
    def jump_to_tocitem(self, item):
        self.jump_to(item.text(1))

    def jump_to_qurl(self, url):
        self.jump_to(url.toString())
        
    def process_toc(self, toc_node, treenode):
        """ Map the epub ToC structure to a Qt tree view."""
        #rowCount = 0 # rows at each level
        for toc_entry in toc_node:
            # print(toc_entry) # debug
            if hasattr(toc_entry, 'title'):
                newRow = qtw.QTreeWidgetItem(treenode)
                newRow.setText(self.SECTION, toc_entry.title)
                newRow.setText(self.HREF, toc_entry.href)
                #self.tocModel.insertRow(rowCount)
                #self.tocModel.setData(
                #    self.tocModel.index(level, rowCount), # self.SECTION),
                #    toc_entry.title)
                #rowCount += 1
            else: # it's a pair of the top level and sub-entries, so recurse
                newRow = qtw.QTreeWidgetItem(treenode)
                newRow.setText(self.SECTION, toc_entry[0].title)
                newRow.setText(self.HREF, toc_entry[0].href)
                #newLevel = qtw.QTreeWidgetItem(treenode)
                self.process_toc(toc_entry[1], newRow) # newLevel
        
    def load_epub(self, filename):
        the_epub = epub.read_epub(filename)
        for k,v in the_epub.__dict__.items():
            print(k, ':', v)
            
        doc_items = the_epub.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        doc_list = list(doc_items)
        for item in doc_list:
            # will I have to make my own dictionary of these?
            print("ITEM", item.file_name)
        #self.tocPane.setPlainText("")
        # suppress "html" namespace prefix.
        ETree.register_namespace('', 'http://www.w3.org/1999/xhtml')
        self.process_toc(the_epub.toc, self.tocPane)
        # TODO: sort list based on TOC. could be return value?
        ch1_text = doc_list[0].get_content().decode('utf-8')
        doc_tree = ETree.fromstring(ch1_text)
        doc_body = doc_tree.find('{http://www.w3.org/1999/xhtml}body')
        for doc in doc_list[1:]:
            text = doc.get_content().decode('utf-8')
            tree = ETree.fromstring(text)
            body = tree.find('{http://www.w3.org/1999/xhtml}body')
            for child in body:
                doc_body.append(child)

        fulltext = ETree.tostring(doc_tree, encoding='unicode')
        #print(fulltext)
        self.mainText.setHtml(fulltext)
        # self.mainText.setHtml(ch1_bytes.decode('utf-8'))
        # good to set this at the end if it fails?
        self.the_epub = the_epub


if __name__ == "__main__":

    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    if len(sys.argv) > 1:
        bookFilename = sys.argv[1]
    else:
        bookFilename = "testbooks/bram-stoker_dracula.epub"
    window.load_epub(bookFilename)

    # this trick passes the app's exit code back to the OS.
    sys.exit(app.exec_())
