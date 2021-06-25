## studious main

import sys
# from Moore's book
from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

# Inheriting from QMainWindow broke the layouts.
class MainWindow(qtw.QMainWindow):
    
    def __init__(self):
        # seems like you always have to call super.__init__ :/
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
        testButton = qtw.QPushButton("Push Me", self)
        textShow = qtw.QTextEdit("some text for starters", self)
        topLayout.addLayout(leftLayout)
        leftLayout.addWidget(testButton)
        leftLayout.addWidget(textShow)

        centerLayout = qtw.QVBoxLayout()
        mainText = qtw.QTextBrowser(self)
        mainText.setSource(qtc.QUrl("testbooks/counselsmaxims.htm"))
        #mainText.setHtml("""
        #   <body>hey <b>There</b>, buddy!<p/>yep.</body>""")
        topLayout.addLayout(centerLayout)
        centerLayout.addWidget(mainText)
        
        # add vertical layout, add widgets to that, rinse and repeat.

        
        # book code calls self.show() here.

if __name__ == "__main__":
    # I wonder how the app can use those arguments!
    app = qtw.QApplication(sys.argv)

    # wait, this is not even relating to the application! I guess it
    # ties into it under the hood. 
    window = MainWindow()
    window.show()

    # this trick passes app exit codes back to the OS.
    sys.exit(app.exec_())
