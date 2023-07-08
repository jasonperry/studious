
# currently just for testing "python src"; package build makes a script.

from studious import studious 
import sys

# it can't find 'run' it when you run it with -m
sys.exit(studious.main())

