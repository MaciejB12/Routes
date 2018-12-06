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
# 1. elementy typu string takie jak: signal, eot, dj pobierać z pliku config
# 2. ochrona boczna - wyszukiwanie ochrony bocznej przez zwrotnicę,
# osobny moduł - in progress, uwaga - wyszukiwanie ochrony bocznej dla zwr powinno
# być realizowane niezależnie od tego czy jest przejezdzana z ostrza czy na ostrze
# 3. pokazać kierunek ustawionej zwrotnicy - w drodze jazdy i w ochr. bocznej
# 4. zrobić helpa - argparse

class BreakFunc(Exception): pass

class Routes(FlankProt):
	
	def __init__(self, fn, ort):
		super().__init__(fn, ort)

	def check_route_end(self, neighb_item, item, name):
		'''sprawdza jakiego typu jest element kończący przebieg'''
		# czy element jest końcem drogi przebiegu (semaforem), 
		if self.elms[item]["type"] == "signal" and \
			self.elms[item]["name"] != name and \
			self.elms[item]["orientation"] == self.ort:
			if self.elms[item]["prot"]: # szukaj urządzeń w drodze ochr.
				self.search_overlap(neighb_item)
			return True
		# czy element jest końcem drogi przebiegu (line interface)
		elif self.elms[item]["type"] == "li":
			return True
		# czy element jest końcem drogi przebiegu (koniec toru)
		elif self.elms[item]["type"] == "eot":
			return True
		return False
		
	def search_elements(self, element, ort):
		'''zasadnicza funkcja do przeszukiwania jsona'''
		nr = self.elms[element]["nr"]
		name = self.elms[element]["name"]
		item = f"element{nr}" # etykieta elementu początkowego
		nxt, last_point, points = "sas2", "", {}

		try:		
			while True:
				self.route[self.elms[item]['name']] = "dj"
				neighb_item = f"element{self.elms[item][nxt]}" # etykieta elementu sas
				if self.check_route_end(neighb_item, item, name):
					nr = self.route_end(element, points, last_point)
					item = f"element{nr}"
					neighb_item = f"element{self.elms[item]['sas2']}"

				if self.elms[item]["type"] == "switch":
					if self.elms[item]["orientation"] == self.ort:
						last_point = self.elms[item]["name"] # ost. zwr. w przebiegu
						
						nxt = self.check_point(points, last_point)
						# ustawienie zwr w drodze jazdy - do modyfikacji
						# print(f"kierunek na zwr {last_point} = {nxt}")
						self.drs[last_point] = nxt
						neighb_item = f"element{self.elms[item][nxt]}"
						
						flank = self.flank_dir(nxt) # kier. szuk. ochr. bocz.

					self.search_flank_prot(item, flank)
				
				flank = self.check_point_dir(neighb_item, nr) # kier. szuk. ochr. bocz.
				nxt, nr, item = self.next_element(neighb_item, nr) # kolejny el.

		except BreakFunc: # jeżeli wyjątek to opuść funkcje i pętle
			print(f"\nKoniec przebiegów od sygnału: {self.elms[element]['name']}")
			
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
		nr = self.elms[element]["nr"]
		item = f"element{nr}"
		self.route[self.elms[item]['name']] = "dj" # ustaw pierwszy el. nowej drogi przebiegu
		return nr
	
	def check_point_dir(self, neighbour, nr):
		'''sprawdza kierunek szukania ochr bocznej kiedy jazda z ostrza'''
		if self.elms[neighbour]["sas2"] == nr:
			return "sas3"
		elif self.elms[neighbour]["sas3"] == nr:
			return "sas2"
		return None

	def write_route(self):
		self.route_list.append(self.route)
		self.drs_list.append(self.drs)
		with open("dict.pkl", "wb") as r:
			pickle.dump(self.route_list, r)
		self.route = OrderedDict()
		with open("dirs.pkl", "wb") as d:
			pickle.dump(self.drs_list, d)
		self.drs = OrderedDict()
			
if __name__== "__main__":
	fn = "routes2.json"
	r = Routes(fn, "P") # kierunek wyszukiwania przebiegów - P lub N

		