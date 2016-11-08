		#| expect os
import os
import sys


		#| expect Hover
class Hover:

	#| expect bool
	is_hovering = True


	is_not_hovering = False

	def grow(self, years):
		print "Growing a potato"


class LocalPotato:
	is_potato = True

			  #| expect LocalPotato
potato = LocalPotato()

 #| expect LocalPotato
potato
