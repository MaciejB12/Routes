#!/usr/bin/env python
# -*- coding: utf-8 -*-
# klasa bazowa routes
# WYKONAWCA: MB
# UTWORZONY: 03-07-2018
# NAZWA: routes_class.py

import json
from flank_prot import FlankProt

# TODO: 
# drogi ochronne za sem. - jako dodatkowy parametr dla sem. 
# że należy zamknąć w drodze ochronnej kolejny element,
# ochrona boczna - wyszukiwanie ochrony bocznej przez zwrotnicę,
# dorobić osobny moduł do tego - importowany

# wyszukiwanie ochrony bocznej na zwr powinno być niezależnie od tego
# czy jest przejezdzana z ostrza czy na ostrze

class BreakFunc(Exception): pass

class Routes(FlankProt):
	
	def __init__(self, filename, orientation):
		super().__init__(filename, orientation)

	def search_elements(self, element, orientation):
		'''zasadnicza funkcja do przeszukiwania jsona'''
		nr = self.elements[element]["nr"]
		name = self.elements[element]["name"]
		item = f"element{nr}" # etykieta elementu początkowego
		next = "sas2"
		points = {}
		last_point = ""
		print("\nPrzebieg: ", end="")
		
		try:
			while True:	
				print(f"{self.elements[item]['name']}, ", end="")
				neighb_item = f"element{self.elements[item][next]}" # etykieta elementu sąsiedniego
				
				# czy element jest końcem drogi przebiegu (np. semaforem), 
				# całego ifa zamknąć w funkcje?
				if self.elements[item]["type"] == "signal" and \
					self.elements[item]["name"] != name and \
					self.elements[item]["orientation"] == self.orientation:

					if self.elements[item]["prot"]: # szukaj urządzeń w drodze ochr.
						self.search_overlap(neighb_item)
					
					nr, next, item = self.route_end(element, points, last_point)
					neighb_item = f"element{self.elements[item][next]}"

				# czy element jest końcem drogi przebiegu (line iface)
				elif self.elements[item]["type"] == "li":
					nr, next, item = self.route_end(element, points, last_point)
					neighb_item = f"element{self.elements[item][next]}"
				
				# czy element jest końcem drogi przebiegu (koniec toru)
				elif self.elements[item]["type"] == "eot":
					nr, next, item = self.route_end(element, points, last_point)
					neighb_item = f"element{self.elements[item][next]}"

				if self.elements[item]["type"] == "switch": # and \
					if self.elements[item]["orientation"] == self.orientation:
						last_point = self.elements[item]["name"] # ost. zwr. w przebiegu
					
						if last_point not in points: # jeżeli ost. zwr. nie ma w points
							points[last_point] = "sas2"
					
						next = points[last_point] # kier. szuk. drogi przeb.
						neighb_item = f"element{self.elements[item][next]}"
						flank = self.flank_dir(next) # kier. szuk. ochr. bocz.
					# self.search_flank_prot(item, flank)
				
					# elif self.elements[item]["type"] == "switch" and \
					# elif self.elements[item]["orientation"] != self.orientation:
					self.search_flank_prot(item, flank)
				
				flank = self.check_point_dir(neighb_item, nr) # kier. szuk. ochr. bocz.
				next, item, nr = self.next_element(neighb_item, nr) # kolejny el.

		except BreakFunc: # jeżeli wyjątek to opuść funkcje i pętle
			print(f"\nKoniec przebiegów rozpoczynających się od sygnału: {self.elements[element]['name']}")
	
	# def flank_dir(self, next):
		# if next == "sas2":
			# return "sas3"
		# elif next == "sas3":
			# return "sas2"
	
	def flank_dir(self, next):
		if next == "sas3":
			return "sas2"
		return "sas3"
	
	def route_end(self, element, points, last_point):
		'''sprawdza ostatnią zwrotnicę w przebiegu, ustawia sąsiedni element dla nowego przebiegu'''
		points = self.check_last_point(points, last_point)
		if not points:
			raise BreakFunc # jeżeli słownik zwrotnic jest pusty to wyjątek
		nr = self.elements[element]["nr"]
		item = f"element{nr}"
		print(f"\nPrzebieg: {self.elements[item]['name']}, ", end="")
		return nr, "sas2", f"element{nr}"
	
	def check_point_dir(self, neighbour, nr):
		'''sprawdza kierunek szukania ochr bocznej kiedy jazda z ostrza'''
		if self.elements[neighbour]["sas2"] == nr:
			return "sas3"
		elif self.elements[neighbour]["sas3"] == nr:
			return "sas2"

if __name__== "__main__":
	filename = "routes2.json"
	r = Routes(filename, "P") # kierunek wyszukiwania przebiegów - P lub N

	
	
	
		