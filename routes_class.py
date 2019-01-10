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
# 2. pokazać kierunek ustawionej zwrotnicy - w drodze jazdy i w ochr. bocznej
# 3. nastawianie zwr jechanych z ostrza
# 4. poprawić zapis do plików pkl
# 5. kryterium zakończenia przebiegów poc. i man.
# 6. zrobić helpa - argparse

class BreakFunc(Exception): pass

class Routes(FlankProt):
	
	def __init__(self, fn, ort):
		super().__init__(fn, ort)
		
	def check_route_end(self, neighb, item, name):
		'''sprawdza jakiego typu jest element kończący przebieg'''
		self.item = self.elms[item]
		# czy element jest końcem drogi przebiegu (semaforem)
		if self.item["type"] == "signal" and self.item["name"] != name and \
			self.item["direct"] == self.ort:			
			if self.item["prot"]: # szukaj w drodze ochr.
				self.search_overlap(neighb)
			return True
		elif self.item["type"] == "li": # line iface
			return True
		elif self.item["type"] == "eot": # kozioł oporowy
			return True
		elif self.item["type"] == "dest": # koniec przebiegu man.
			return True
		return False
		
	def search_elements(self, element, ort):
		'''główna funkcja do przeszukiwania jsona/yamla'''
		elem = self.elms[element]
		nr = elem["nr"]
		name = elem["name"]
		item = f"elem{nr}" # etykieta elem. pocz.
		nxt, last_point, points = "sas2", "", OrderedDict()

		try:		
			while True:
				self.routes.append((self.item["name"], "dj"))
				neighb = f"element{self.item[nxt]}" # etykieta sąsiedniego el.
				if self.check_route_end(neighb, item, name):
					nr = self.route_end(element, points, last_point)
					item = f"elem{nr}"
					neighb = f"elem{self.item['sas2']}"

				if self.item["type"] == "switch":
					if self.item["direct"] == self.ort:
						last_point = self.item["name"] # ost. zwr. w przebiegu
						nxt = self.check_point(points, last_point)
						# dodaj el. do listy zwr. kierunkowych
						self.directs.append((last_point, nxt)) 
						neighb = f"element{self.item[nxt]}"
						# kier. szuk. ochr. bocz.
						flank = self.flank_dir(nxt) 
					self.search_flank_prot(item, flank)

				flank = self.check_point_dir(neighb, nr) # kier. szuk. ochr. bocz.
				nxt, nr, item = self.next_element(neighb, nr) # kolejny el.
		# opuść funkcje 
		except BreakFunc:
			print(f"\nKoniec przebiegów od sygnału: {self.elms[element]['name']}")
			
	def flank_dir(self, nxt):
		if nxt == "sas3":
			return "sas2"
		return "sas3"
	
	def route_end(self, elem, points, last_point):
		'''sprawdza ost. zwrotnicę w przebiegu, ustawia sąsiedni element
		dla nowego przebiegu'''
		points = self.check_last_point(points, last_point)
		self.write_route()
		self.routes.append(f"Przebieg {self.n}")
		self.directs.append(f"Przebieg {self.n}")
		self.n += 1
		if not points:
			raise BreakFunc # jeżeli słownik zwrotnic jest pusty to wyjątek
		
		nr = self.elms[elem]["nr"]
		item = f"element{nr}"
		self.route_list.append((self.item["name"], "dj"))  # 1 el. nast. przebiegu
		return nr
	
	def check_point_dir(self, neighb, nr):
		'''sprawdza kierunek szukania ochr bocznej kiedy jazda z ostrza'''
		neighb = self.elms[neighb]
		if neighb["sas2"] == nr:
			return "sas3"
		elif neighb["sas3"] == nr:
			return "sas2"
		return None

	def write_route(self):
		'''zapis do pkl - do poprawy - powtórzenia'''
		with open("dict.pkl", "wb") as r:
			pickle.dump(self.route_list, r)
		with open("dirs.pkl", "wb") as d:
			pickle.dump(self.drs_list, d)
			
if __name__== "__main__":
	fn = "routes2.json"
	r = Routes(fn, "P")

		