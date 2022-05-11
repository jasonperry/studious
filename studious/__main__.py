
# OK to do this right?
from studious import *
import sys

app = qtw.QApplication(sys.argv)
window = MainWindow()
if len(sys.argv) > 1:
    bookFilename = sys.argv[1]
    window.load_epub(bookFilename)
    # this trick passes the app's exit code back to the OS.
sys.exit(app.exec_())
