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
# 2. nastawianie zwr jechanych z ostrza
# 3. pokazywać kierunek nast. wszystkich zwr w drodze jazdy i ochr.
# 4. kryterium zakończenia przebiegów poc. i man.
# 5. zrobić helpa - argparse

class BreakFunc(Exception): pass

class Routes(FlankProt):
	
	def __init__(self, fn, conf, ort):
		super().__init__(fn, conf, ort)
		
	def check_route_end(self, neighb, item, name):
		'''sprawdza jakiego typu jest element kończący przebieg'''
		item = self.elms[item]
		# czy element jest sygnałem końcowym
		if item["type"] == "signal" and item["name"] != name and \
			item["direct"] == self.ort:
			if item["prot"]: # szukaj w drodze ochr.
				self.search_overlap(neighb)
			return True
		elif item["type"] == "li":   # line iface
			return True
		elif item["type"] == "eot":  # kozioł oporowy
			return True
		elif item["type"] == "dest": # koniec przebiegu man.
			return True
		return False
		
	def search_elements(self, element, ort):
		'''główna funkcja do przeszukiwania jsona/yamla'''
		elem = self.elms[element]
		nr = elem["nr"]
		name = elem["name"]
		item = element # element{nr} etykieta elem. pocz.
		# self.item = self.elms[item]
		nxt, last_point, points = "sas2", "", OrderedDict()
		try:
			while True:
				it = self.elms[item]
				self.routes.append((it["name"], "dj"))
				neighb = f"element{it[nxt]}" # etykieta el. sąs.
				if self.check_route_end(neighb, item, name):
					nr = self.route_end(element, points, last_point)
					item = f"element{nr}"
					neighb = f"element{self.elms[item]['sas2']}"

				if it["type"] == "switch":
					if it["direct"] == self.ort:
						last_point = it["name"] # ost. zwr. w przebiegu
						nxt = self.check_point(points, last_point)
						# dodaj el. do listy zwr. kierunkowych
						self.directs.append((last_point, nxt)) 
						neighb = f"element{it[nxt]}"
						# kier. szuk. ochr. bocz.
						flank = self.flank_dir(nxt) 
					self.search_flank_prot(item, flank)

				flank = self.check_point_dir(neighb, nr) # kier. szuk. ochr. bocz.
				nxt, nr, item = self.next_element(neighb, nr) # kolejny el.

		except KeyError as err:
			print(f"Key Error: {err}")
		except BreakFunc:
			print(f"\nKoniec przebiegów od sygnału: {elem['name']}")
	
	def route_end(self, elem, points, last_point):
		'''sprawdza ost. zwrotnicę w przebiegu, ustawia sąsiedni element
		dla nowego przebiegu'''
		points = self.check_last_point(points, last_point)
		d = {"dict.pkl": self.routes, "dirs.pkl": self.directs}
		for i in d:
			self.write(i, d[i])
		for i in d:
			d[i].append(f"Przebieg {self.n}")
		self.n += 1
		if not points:
			raise BreakFunc # jeżeli słownik zwrotnic jest pusty to wyjątek
		
		nr = self.elms[elem]["nr"]
		item = f"element{nr}"
		d["dict.pkl"].append((self.elms[item]["name"], "dj"))  # 1 el. nast. przebiegu
		return nr
	
	def check_point_dir(self, neighb, nr):
		'''sprawdza kierunek szukania ochr bocznej kiedy jazda z ostrza'''
		neighb = self.elms[neighb]
		if neighb["sas2"] == nr:
			return "sas3"
		elif neighb["sas3"] == nr:
			return "sas2"
		return None
	
	def flank_dir(self, nxt):
		if nxt == "sas3":
			return "sas2"
		return "sas3"
	
	def write(self, file, obj):
		with open(file, "wb") as f:
			pickle.dump(obj, f)
			
if __name__== "__main__":
	fn = "routes2.json"
	r = Routes(fn, "P")

		