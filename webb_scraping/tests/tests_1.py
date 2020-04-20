import os
import sys
sys.path.append(os.getcwd()[:-6])
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
# sys.path.insert(0, os.getcwd()) 
# parent_dir = os.path.dirname(current_dir)
# current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class TestImports(unittest.TestCase):

	def test_calculations_import(self):
		import webb_scraping.calculations as c

	def test_target_import(self):
		import webb_scraping.target as t

class TestWebb(unittest.TestCase):
	import webb_scraping.target as t
	import webb_scraping.calculations as c

	def test_webb_approved(self):
		"""
		Take a random assortment of stars and ensure that they are
		webb-approved if they are supposed to be.
		"""
		stars = ['GJ 357']
		stars_webb_approved = []
		expected_stars_webb_approved = [True]
		for star in stars:
			star_target = t.Target(star)
			star_target.scape_webb_MAST()
			stars_webb_approved.append(star_target.webb_approved)

		self.assertItemsEqual(stars_webb_approved, expected_stars_webb_approved)