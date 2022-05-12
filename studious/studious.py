#!/usr/bin/env python3

## studious main

import sys
import hashlib
from base32c import cb32encode
# from Moore's book
from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc
# from PySide2 import QtWebEngineWidgets as qtwe

import ebooklib
from ebooklib import epub

import xml.etree.ElementTree as ETree

_debug = False
_dumpHTML = False

def unique_list(l):
    ulist = []
    for item in l:
        if item not in ulist:
            ulist.append(item)
    return ulist


class EPubTextBrowser(qtw.QTextBrowser):
    """Derived QTW class for the main text view."""
    def set_epub(self, the_epub):
        self.the_epub = the_epub

    def loadResource(self, restype, url):
        """Override to load images that are within the epub."""
        if restype == 2 and url.isRelative():
            if _debug:
                print("Image resource found: ", url.toDisplayString())
            # get file part of it. OR, load as path from zip?
            # for now, assume filename part of URL is the ID.
            imgHref = url.toDisplayString()
            if imgHref.startswith("../"):
                imgHref = imgHref[3:]
            image = self.the_epub.get_item_with_href(imgHref)
            # image = self.the_epub.get_item_with_id(url.fileName())
            if image:
                if _debug:
                    print("successfully loaded image of type", type(image))
                image = qtg.QImage.fromData(image.get_content())
                if image.width() > (self.width() * 0.8):
                    image = image.scaledToWidth(
                        self.width() * 0.8,
                        mode=qtc.Qt.TransformationMode.SmoothTransformation)
                # It accepts anything as the variant! Python!
                return image
            else:
                print("image load failed:", imgHref)
            # should we fetch external images? maybe not
        if _debug:
            print("loading non-image resource", url)
        super(EPubTextBrowser, self).loadResource(restype, url)
        
# Inheriting from QMainWindow broke the layouts.
# Should I make another class for the book itself?
class MainWindow(qtw.QMainWindow):
    """UI Class for the Studious epub reader"""
    SECTION = 0 # constants for the treeview
    HREF = 1

   
    def __init__(self):
        """GUI Layout is built here."""
        # The book doesn't pass the class and object.
        super(MainWindow, self).__init__()

        # I won't call these if I set it up myself.
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        window = qtw.QWidget()
        self.setCentralWidget(window)
        
        self.setWindowTitle("Studious Reader")
        self.resize(960,600)

        ### Menu items
        openPixmap = getattr(qtw.QStyle, 'SP_DialogOpenButton')
        openIcon = self.style().standardIcon(openPixmap)
        openAction = qtw.QAction(openIcon, '&Open', self)
        openAction.setShortcut(qtg.QKeySequence("Ctrl+o"))
        openAction.triggered.connect(self.open_new_file)
        menuBar = qtw.QMenuBar(self)
        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(openAction)
        self.setMenuBar(menuBar)

        ### The tricky layout to get the panes to work correctly.
        topLayout = qtw.QHBoxLayout()
        window.setLayout(topLayout)
        
        leftLayout = qtw.QVBoxLayout()
        topLayout.addLayout(leftLayout)
        leftSplitter = qtw.QSplitter(self) # or add to top hlayout?
        leftLayout.addWidget(leftSplitter)

        self.tocPane = qtw.QTreeWidget(self)
        self.tocPane.setColumnCount(2)
        self.tocPane.setHeaderLabels(["Section", "Link"])
        if not _debug:
            self.tocPane.hideColumn(1)
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

        self.mainText = EPubTextBrowser(self) #qtw.QTextBrowser(self)
        # this isn't doing anything, is it reading the css instead?
        #self.mainText.style = """
        #  <style>body{ margin-left: 60px; margin-right: 60px; line-height: 130% }</style>
        #"""
        self.mainText.document().setDefaultStyleSheet(
            'body{ margin-left: 20px; margin-right: 20px; line-height: 110% }')
        mainText_font = qtg.QFont('Liberation Serif', 12)
        mainText_font.setStyleHint(qtg.QFont.Serif)
        self.mainText.setFont(mainText_font)
        self.mainText.setOpenLinks(False)
        self.mainText.anchorClicked.connect(self.jump_to_qurl)
        self.mainText.cursorPositionChanged.connect(self.update_location)
        rightHLayout.addWidget(self.mainText) # 1
        # rightSplitter.addWidget(self.mainText) # 2
        # centerLayout.addWidget(self.mainText) # 3

        # horizontal and vertical is flipped from what I thought.
        self.mainText.setFixedWidth(500)
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

    def open_new_file(self):
        filePath, _ = qtw.QFileDialog.getOpenFileName(
            self, caption="Load new ebook", filter="EPub files (*.epub)")
        self.load_epub(filePath)
        
    def update_location(self):
        print("Cursor position:", self.mainText.textCursor().position())

    #def create_toc_model(self, parent):
    #    model = qtg.QStandardItemModel(0, 1, parent)
    #    # can I just define constants like this?
    #    model.setHeaderData(self.SECTION, qtc.Qt.Horizontal, "Section")
    #    return model

    def jump_to(self, urlStr):
        """Jump to an internal link. May refer to a separate page in the 
        original epub, or to an anchor."""
        if _debug:
            print("Jumping to", urlStr)
        splitUrl = urlStr.split('#')
        href = splitUrl[0]
        # sectionText = self.the_epub.get_item_with_href(href).get_content()
        # self.mainText.setHtml(sectionText.decode('utf-8'))
        if len(splitUrl) > 1:
            self.mainText.scrollToAnchor(splitUrl[1])
            if _debug:
                print("ANCHORJUMP", splitUrl[1])
        else:
            if _debug:
                print("URLJUMP:", urlStr)
            self.mainText.scrollToAnchor(urlStr)
        # Update cursor position by moving the cursor to where we are
        # and getting its location.
        #  or should I do that only when they click?
        # TODO: move TOC highlight to wherever I jumped to
        #  (probably with a trigger for the scroll event, because
        #   it should work for scrolling too)
        browserRect = self.mainText.rect()
        newCursor = self.mainText.cursorForPosition(browserRect.topLeft())
        #newcursor = self.mainText.cursorForPosition(qtc.QPoint(0,0))
        self.mainText.setTextCursor(newCursor)
        if _debug:
            print("new cursor rect position:", self.mainText.cursorRect())
            print("Cursor position:", self.mainText.textCursor().position())
    
    def jump_to_tocitem(self, item):
        """Jump for a click in the Contents pane."""
        self.jump_to(item.text(1))

    def jump_to_qurl(self, url):
        # TODO: popup asking if want to open in browser
        if url.isRelative():
            self.jump_to(url.toString())
        
    def process_toc(self, toc_node, treenode):
        """ Map the epub ToC structure to a Qt tree view."""
        # rowCount = 0 # rows at each level
        # store and return hrefs for the correct ordering
        # hrefs = []
        filename_anchors = False
        for toc_entry in toc_node:
            if _debug:
                print(type(toc_entry)) # epub.Link or tuple
            if hasattr(toc_entry, 'title'):
                if _debug:
                    print(toc_entry.__dict__)
                newRow = qtw.QTreeWidgetItem(treenode)
                newRow.setText(self.SECTION, toc_entry.title)
                entry_href = toc_entry.href
                if entry_href.startswith('xhtml/'):
                    entry_href = entry_href[6:]
                newRow.setText(self.HREF, entry_href)
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
                if _debug:
                    print("tuple[0] is", type(toc_entry[0]))
                    print(toc_entry[0].__dict__)
                newRow.setText(self.SECTION, toc_entry[0].title)
                entry_href = toc_entry[0].href
                if entry_href.startswith('xhtml/'):
                    entry_href = entry_href[6:]
                newRow.setText(self.HREF, entry_href)
                #newLevel = qtw.QTreeWidgetItem(treenode)
                # hrefs += self.process_toc(toc_entry[1], newRow) # newLevel
                filename_anchors |= self.process_toc(toc_entry[1], newRow)
                newRow.setExpanded(True)
        return filename_anchors

    def load_notes(self, bookfilename, author_last):
        '''Load the notes file corresponding to a book's hash into the
        notes pane.'''
        hasher = hashlib.sha256()
        bookfile = open(bookfilename, 'rb')
        hasher.update(bookfile.read())
        bookfile.close()
        b32str = cb32encode(hasher.digest()[:10])
        print("hash encode: ", author_last[:3] + '_' + b32str)
    
    
    def load_epub(self, filename):
        '''Load epub content, and also call out to generate the TOC and
        load the notes file.'''
        the_epub = epub.read_epub(filename)
        self.mainText.set_epub(the_epub) # have to set early
        #for k,v in the_epub.__dict__.items():
        #    print(k, ':', v)
            
        #doc_items = the_epub.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        #doc_list = list(doc_items)
        all_items = the_epub.get_items()
        #for item in list(all_items):
            # will I have to make my own dictionary of these?
            # print("ITEM", item.file_name, item.get_id(), item.get_type())

        if _debug:
            print(the_epub.spine)
        self.tocPane.clear()
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
        for uid, linear in the_epub.spine: # [1:] # file_hrefs[1:]:
            # TODO: if it's not linear, put it at the end.
            if _debug:
                print("LOADITEM:", uid)
            the_item = the_epub.get_item_with_id(uid)
            text = the_item.get_content().decode('utf-8')
            tree = ETree.fromstring(text)
            body = tree.find('{http://www.w3.org/1999/xhtml}body')
            # body.insert (anchor element, 0)?
            # create div elements with the name corresponding to the file
            if filename_anchors: 
                # tried 'name' and 'id'
                item_name = the_item.get_name()
                if item_name.startswith('xhtml/'):
                    item_name = item_name[6:]
                toc_div = ETree.Element('div', {'id': item_name})
                if _debug:
                    print("ANCHOR ADDED:", list(toc_div.items()))
                for child in body:
                    # why is 0 okay?
                    #toc_div.insert(0, child)
                    toc_div.append(child)
                    # print("CHILD ADDED")
                doc_body.append(toc_div)
            else:
                for child in body:
                    doc_body.append(child)
        fulltext = ETree.tostring(doc_tree, encoding='unicode')
        self.mainText.setHtml(fulltext)
        if _dumpHTML:
            print(fulltext)
        # TODO: have spinny until finished loading, so it won't be
        #  unresponsive (see the Bible)
        # this lies, it says before finished loading images
        print("load finished.") 
        author_full = the_epub.get_metadata("http://purl.org/dc/elements/1.1/", "creator")[0][0]
        author_last = author_full.split()[-1].lower()
        print(author_last)
        self.load_notes(filename, author_last)


# if __name__ == "__main__":
def main():
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    if len(sys.argv) > 1:
        bookFilename = sys.argv[1]
        window.load_epub(bookFilename)
    # this trick passes the app's exit code back to the OS.
    sys.exit(app.exec_())
