## studious main

import sys
# from Moore's book
from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

import ebooklib
from ebooklib import epub

import xml.etree.ElementTree as ETree

def unique_list(l):
    ulist = []
    for item in l:
        if item not in ulist:
            ulist.append(item)
    return ulist

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
        topLayout.addLayout(leftLayout)
        leftSplitter = qtw.QSplitter(self) # or add to top hlayout?
        leftLayout.addWidget(leftSplitter)

        self.tocPane = qtw.QTreeWidget(self)
        self.tocPane.setColumnCount(2)
        self.tocPane.setHeaderLabels(["Section", "Link"])
        # self.tocPane.hideColumn(1)  # leaving visible for devel
        self.tocPane.itemClicked.connect(self.jump_to_tocitem)
        #leftLayout.addWidget(self.tocPane)
        leftSplitter.addWidget(self.tocPane)

        ## 1. use a new hbox layout to have no splitter on the right
        rightFrame = qtw.QFrame(self)
        ## these didn't make any difference at all.
        # rightFrame.setFrameStyle(qtw.QFrame.NoFrame)
        # rightFrame.setContentsMargins(qtc.QMargins(0,0,0,0))
        leftSplitter.addWidget(rightFrame)
        rightHLayout = qtw.QHBoxLayout()
        rightFrame.setLayout(rightHLayout)

        ## 2. sub-splitter on the right
        # rightSplitter = qtw.QSplitter(self)
        # leftSplitter.addWidget(rightSplitter)
        ## 2a. to have the right splitter be separate
        # topLayout.addWidget(rightSplitter)

        ## 3. just 3 vboxes, no splitters
        # centerLayout = qtw.QVBoxLayout()
        # topLayout.addLayout(centerLayout)

        self.mainText = qtw.QTextBrowser(self)
        # this isn't doing anything, is it reading the css instead?
        self.mainText.style = """
          <style>body{ margin: 30px; line-height: 130% }</style>
        """
        mainText_font = qtg.QFont('Liberation Serif', 11)
        mainText_font.setStyleHint(qtg.QFont.Serif)
        self.mainText.setFont(mainText_font)
        self.mainText.setOpenLinks(False)
        self.mainText.anchorClicked.connect(self.jump_to_qurl)
        self.mainText.cursorPositionChanged.connect(self.update_location)
        rightHLayout.addWidget(self.mainText) # 1
        # rightSplitter.addWidget(self.mainText) # 2
        # centerLayout.addWidget(self.mainText) # 3

        # horizontal and vertical is flipped from what I thought.
        self.mainText.setFixedWidth(400)
        # this has no effect if fixedwidth is set.
        # and it doesn't stick to preferred if there's a splitter.
        self.mainText.setSizePolicy(qtw.QSizePolicy.Maximum,
                                     qtw.QSizePolicy.Preferred)

        # will need this vboxlayout if we add something below the notes.
        # rightLayout = qtw.QVBoxLayout()
        self.notesFrame = qtw.QTextEdit(self)
        # topLayout.addLayout(rightLayout)
        # rightHLayout.addLayout(rightLayout)   # 1
        rightHLayout.addWidget(self.notesFrame) # 1 no layout
        # rightSplitter.addWidget(self.notesFrame) # 2 
        # rightLayout.addWidget(self.notesFrame) # 3

        self.show()

    def update_location(self):
        print("Cursor position:", self.mainText.textCursor().position())

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
            #print("url with no anchor...problem...")
            self.mainText.scrollToAnchor(urlStr)
        # TODO: move TOC highlight to wherever I jumped to
        #  (probably with a trigger for the scroll event)
        # first step: move the cursor to where we are and get its location.
        #  or should I do that only when they click?
        browserRect = self.mainText.rect()
        newCursor = self.mainText.cursorForPosition(browserRect.topLeft())
        #newcursor = self.mainText.cursorForPosition(qtc.QPoint(0,0))
        self.mainText.setTextCursor(newCursor)
        print("new cursor rect position:", self.mainText.cursorRect())
        print("Cursor position:", self.mainText.textCursor().position())
    
    def jump_to_tocitem(self, item):
        self.jump_to(item.text(1))

    def jump_to_qurl(self, url):
        # TODO: if it's not a local file one, don't jump, just ignore
        #  (or open in browser)
        self.jump_to(url.toString())
        
    def process_toc(self, toc_node, treenode):
        """ Map the epub ToC structure to a Qt tree view."""
        # rowCount = 0 # rows at each level
        # store and return hrefs for the correct ordering
        # hrefs = []
        filename_anchors = False
        for toc_entry in toc_node:
            # print(type(toc_entry)) # epub.Link or tuple
            if hasattr(toc_entry, 'title'):
                # print(toc_entry.__dict__)
                newRow = qtw.QTreeWidgetItem(treenode)
                newRow.setText(self.SECTION, toc_entry.title)
                newRow.setText(self.HREF, toc_entry.href)
                if len(toc_entry.href.split('#')) < 2:
                    filename_anchors = True
                #newRow.setExpanded(True)
                ## leaving this here in case we ever need a custom model?
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
                # hrefs += self.process_toc(toc_entry[1], newRow) # newLevel
                filename_anchors |= self.process_toc(toc_entry[1], newRow)
                newRow.setExpanded(True)
        return filename_anchors

    
    def load_epub(self, filename):
        the_epub = epub.read_epub(filename)
        #for k,v in the_epub.__dict__.items():
        #    print(k, ':', v)
            
        #doc_items = the_epub.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        #doc_list = list(doc_items)
        # all_items = the_epub.get_items()
        # for item in list(all_items):
            # will I have to make my own dictionary of these?
            # print("ITEM", item.file_name, item.get_id(), item.get_type())
        #file_hrefs = unique_list(self.process_toc(the_epub.toc, self.tocPane))

        print(the_epub.spine)
        filename_anchors = self.process_toc(the_epub.toc, self.tocPane)
        if filename_anchors:
            print("epub has toc links with filename only")

        # suppress "html" namespace prefix.
        ETree.register_namespace('', 'http://www.w3.org/1999/xhtml')
        # TODO: loop to get the first item that's linear.
        first_item = the_epub.get_item_with_id(the_epub.spine[0][0])
        # merge all the HTML file bodies into one.
        first_text = first_item.get_content().decode('utf-8')
        doc_tree = ETree.fromstring(first_text)
        doc_body = doc_tree.find('{http://www.w3.org/1999/xhtml}body')
        for uid, linear in the_epub.spine[1:]: # file_hrefs[1:]:
            # TODO: if it's not linear, put it at the end.
            the_item = the_epub.get_item_with_id(uid)
            text = the_item.get_content().decode('utf-8')
            tree = ETree.fromstring(text)
            body = tree.find('{http://www.w3.org/1999/xhtml}body')
            # body.insert (anchor element, 0)?
            if filename_anchors:
                toc_anchor = ETree.Element('a', {'name': the_item.get_name()})
                doc_body.append(toc_anchor)
            for child in body:
                doc_body.append(child)

        fulltext = ETree.tostring(doc_tree, encoding='unicode')
        self.mainText.setHtml(fulltext)
        print("Cursor position:", self.mainText.cursorRect())
        # print(fulltext)
        # good to set this at the end, in case it fails?
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
