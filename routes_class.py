#!/usr/bin/env python
# -*- coding: utf-8 -*-
# klasa bazowa routes - zasadniczy moduł wyszukiwania dróg przebiegu
# WYKONAWCA: MB
# UTWORZONY: 03-07-2018
# NAZWA: routes_class.py

import json
import pickle
from collections import OrderedDict

from flank_prot import FlankProt

# TODO: 
# 1. elementy typu string taie jak: signal, eot, dj pobierać z pliku config
# 2. ochrona boczna - wyszukiwanie ochrony bocznej przez zwrotnicę,
# osobny moduł - in progress, uwaga - wyszukiwanie ochrony bocznej dla zwr powinno
# być realizowane niezależnie od tego czy jest przejezdzana z ostrza czy na ostrze
# 3. argparse - help

class BreakFunc(Exception): pass

class Routes(FlankProt):
	
	def __init__(self, fn, ort):
		super().__init__(fn, ort)

	def check_route_end(self, neighb_item, item, name):
		'''sprawdza jakiego typu jest element kończący przebieg'''
		# czy element jest końcem drogi przebiegu (semaforem), 
		if self.elements[item]["type"] == "signal" and \
			self.elements[item]["name"] != name and \
			self.elements[item]["orientation"] == self.ort:
			if self.elements[item]["prot"]: # szukaj urządzeń w drodze ochr.
				self.search_overlap(neighb_item)
			return True
		# czy element jest końcem drogi przebiegu (line interface)
		elif self.elements[item]["type"] == "li":
			return True
		# czy element jest końcem drogi przebiegu (koniec toru)
		elif self.elements[item]["type"] == "eot":
			return True
		return False
		
	def search_elements(self, element, ort):
		'''zasadnicza funkcja do przeszukiwania jsona'''
		nr = self.elements[element]["nr"]
		name = self.elements[element]["name"]
		item = f"element{nr}" # etykieta elementu początkowego
		nxt = "sas2"
		points = {}
		last_point = ""

		try:		
			while True:
				self.route[self.elements[item]['name']] = "dj"
				neighb_item = f"element{self.elements[item][nxt]}" # etykieta elementu sas
				if self.check_route_end(neighb_item, item, name):
					nr = self.route_end(element, points, last_point)
					item = f"element{nr}"
					neighb_item = f"element{self.elements[item]['sas2']}"

				if self.elements[item]["type"] == "switch":
					if self.elements[item]["orientation"] == self.ort:
						last_point = self.elements[item]["name"] # ost. zwr. w przebiegu
						
						nxt = self.check_point(points, last_point)
						neighb_item = f"element{self.elements[item][nxt]}"
						
						flank = self.flank_dir(nxt) # kier. szuk. ochr. bocz.
					# elif self.elements[item]["orientation"] != self.ort:
					#	flank = self.check_point_dir(neighb_item, nr)
					self.search_flank_prot(item, flank)
				
				flank = self.check_point_dir(neighb_item, nr) # kier. szuk. ochr. bocz.
				nxt, nr, item = self.next_element(neighb_item, nr) # kolejny el.

		except BreakFunc: # jeżeli wyjątek to opuść funkcje i pętle
			print(f"\nKoniec przebiegów od sygnału: {self.elements[element]['name']}")
			
	def flank_dir(self, nxt):
		if nxt == "sas3":
			return "sas2"
		return "sas3"
	
	def route_end(self, element, points, last_point):
		'''sprawdza ost. zwrotnicę w przebiegu, ustawia sąsiedni element
		dla nowego przebiegu'''
		points = self.check_last_point(points, last_point)
		self.write_route()
		if not points:
			raise BreakFunc # jeżeli słownik zwrotnic jest pusty to wyjątek
		nr = self.elements[element]["nr"]
		item = f"element{nr}"
		self.route[self.elements[item]['name']] = "dj" # ustaw pierwszy el. nowej drogi przebiegu
		return nr
	
	def check_point_dir(self, neighbour, nr):
		'''sprawdza kierunek szukania ochr bocznej kiedy jazda z ostrza'''
		if self.elements[neighbour]["sas2"] == nr:
			return "sas3"
		elif self.elements[neighbour]["sas3"] == nr:
			return "sas2"
		return None

	def write_route(self):
		self.route_list.append(self.route)
		with open("dict.pkl", "wb") as p:
			pickle.dump(self.route_list, p)
		self.route = OrderedDict()
			
if __name__== "__main__":
	fn = "routes2.json"
	r = Routes(fn, "P") # kierunek wyszukiwania przebiegów - P lub N

	
	
	
		