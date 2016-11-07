		#| expect os
import os
import sys

		#| expect Potato
class Potato:

	#| expect is_tuber
	is_tuber = True

	def grow(self, years):
		print "Growing a potato"


			  #| expect Potato
potato = Potato()

 #| expect Potato
potato
