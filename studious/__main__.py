
# OK to do this right?
import studious 
import sys

# wheel says a "def main():" is needed for a console script

# it can't find 'run' it when you run it with -m
studious.main()

#app = qtw.QApplication(sys.argv)
#window = MainWindow()
#if len(sys.argv) > 1:
#    bookFilename = sys.argv[1]
#    window.load_epub(bookFilename)
#    # this trick passes the app's exit code back to the OS.
#sys.exit(app.exec_())
