"""python3 rooms/build.py <room> [--quick] [--nonight]"""
import sys, os, importlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
name = sys.argv[1]
lib.reset()
R = importlib.import_module('r_' + name).make()
lib.build(R, quick='--quick' in sys.argv, night='--nonight' not in sys.argv)
