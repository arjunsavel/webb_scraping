import os
import sys
sys.path.append(os.getcwd()[:-6])
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
# sys.path.insert(0, os.getcwd()) 
# parent_dir = os.path.dirname(current_dir)
# current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))



class TestImports(unittest.TestCase):

	def test_calculations_import(self):
		from webb_scraping import calculations

	def test_target_import(self):
		from webb_scraping import target