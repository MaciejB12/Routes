#!/usr/bin/env python
# -*- coding: utf-8 -*-
# klasa bazowa routes
# WYKONAWCA: MB
# UTWORZONY: 03-07-2018
# NAZWA: Routes_class.py

import json

class BreakFunc(Exception): pass

class Routes:
	
	def __init__(self, filename, position):
		with open(filename, "r") as f:
			elements_file = json.load(f)
		self.elements = elements_file["routes"]
		self.position = position
		
	def search_elements(self, element, position):
		'''zasadnicza funkcja do przeszukiwania jsona'''
		nr = self.elements[element]["nr"]
		name = self.elements[element]["name"]
		item = f"element{nr}" # etykieta elementu początkowego
		next = "sas2"
		points = {}
		last_point = ""
		print("\nRoute: ", end="")
		
		try:
			while True:
				print(f"{self.elements[item]['name']} ", end="") # drukuj kolejny element
				neighb_item = f"element{self.elements[item][next]}" # etykieta elementu sąsiedniego
				
				# sprawdzamy czy element jest końcem drogi przebiegu (signal)
				if self.elements[item]["type"] == "signal" and \
					self.elements[item]["name"] != name and \
					self.elements[item]["position"] == self.position:
					
					next, nr, item = self.route_end(element, points, last_point)
					neighb_item = f"element{self.elements[item][next]}"
				
				# sprawdzamy czy element jest końcem drogi przebiegu (line iface)
				elif self.elements[item]["type"] == "li":
					
					next, nr, item = self.route_end(element, points, last_point)
					# points = check_last_point(points, last_point)
					neighb_item = f"element{self.elements[item][next]}"
			
				if self.elements[item]["type"] == "switch" and \
					self.elements[item]["position"] == self.position:
					
					last_point = self.elements[item]["name"]
					if last_point not in points:
						points[last_point] = "sas2"
					next = points[last_point]
					neighb_item = f"element{self.elements[item][next]}"
					
				next = self.check_element_direction(neighb_item, nr)
				nr = self.elements[neighb_item]["nr"]
				item = f"element{nr}"
		
		except BreakFunc: # jeżeli wyjątek to opuść funkcje i pętle
			print(f"\nEnd of routes beginning from signal: {self.elements[element]['name']}")

	def route_end(self, element, points, last_point):
		'''sprawdza ostatnią zwrotnicę w przebiegu ustawia sąsiedni element'''
		points = self.check_last_point(points, last_point)
		if not points:
			raise BreakFunc # jeżeli słownik zwrotnic jest pusty to wyjątek
		nr = self.elements[element]["nr"]
		item = f"element{nr}"
		print(f"\nRoute: {self.elements[item]['name']} ", end="")
		return "sas2", nr, f"element{nr}"
	
	def check_element_direction(self, neighbour, nr):
		'''sprawdza czy sąsiedni element nie wskazuje na poprzedni, zwraca sąsiada'''
		if self.elements[neighbour]["sas2"] == nr or \
			self.elements[neighbour]["sas3"] == nr:
			return "sas1"
		return "sas2"
	
	def check_last_point(self, switches, last_switch):
		'''sprawdza czy jest jakaś zwrotnica w przebiegu 
		i aktualne położenie ostatniej zwrotnicy w przebiegu'''
		if any(switches):
			if switches[last_switch] == "sas2":
				switches[last_switch] = "sas3"
			else:
				if all(i == "sas3" for i in switches.values()):
					switches = {}
				else:
					switches.pop(last_switch)
		return switches

if __name__== "__main__":
	filename = "routes.json"
	r = Routes(filename, "P")

	
	
	
		