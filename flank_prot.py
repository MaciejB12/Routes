#!/usr/bin/env python
# -*- coding: utf-8 -*-
# moduł wyszukiwania ochrony bocznej i drogi ochronnej
# WYKONAWCA: MB
# UTWORZONY: 09-07-2018
# NAZWA: flank_prot.py

import json

class BreakFunc(Exception): pass

class FlankProt:
	
	def __init__(self, filename, orientation):
		with open(filename, "r") as f:
			elements_file = json.load(f)
		self.elements = elements_file["routes"]
		self.orientation = orientation
	
	def search_overlap(self, neighbour):
		'''szuka drogi ochronnej (nast. el. za sem. koncowym drogi przebiegu)'''
		print(f"{self.elements[neighbour]['name']} w drodze ochronnej")
				
	def search_flank_prot(self, start_item, start_next):
		pos = self.elements[start_item]["orientation"]
		nr = self.elements[start_item]["nr"]
		next = start_next
		item = start_item
		if pos == "N":
			op_pos = "P"
		else:
			op_pos = "N"
		points = {}
		last_point = {}
		try:
			while True:
				neighb_item = f"element{self.elements[item][next]}"
				# czy element jest semaforem skierowanym w dobrą stronę - może dawać ochr. boczną
				if self.elements[item]["type"] == "signal" and \
					next == "sas1":
					print(f"sem {self.elements[item]['name']} w ochr. bocz.", end="")
					nr, item, points = self.flank_end(start_item, points, last_point)
					neighb_item = f"element{self.elements[item][start_next]}"
				# czy element jest zwr skierowaną w dobrą stronę - może dawać ochr. boczną
				elif self.elements[item]["type"] == "switch" and \
					self.elements[item]["orientation"] == op_pos:
					print(f"zwr {self.elements[item]['name']} w ochr. bocz.", end="")
					nr, item, points = self.flank_end(start_item, points, last_point)
					neighb_item = f"element{self.elements[item][start_next]}"
				# czy element jest końcem toru
				elif self.elements[item]["type"] == "eot":
					nr, item, points = self.flank_end(start_item, points, last_point)
					neighb_item = f"element{self.elements[item][start_next]}"
				#else:
				#	print(f"{item}, Nie znaleziono elementu ochrony bocznej")
				
				if self.elements[item]["type"] == "switch" and \
					self.elements[item]["orientation"] == pos and \
					item != start_item:
					last_point = self.elements[item]["name"]
					
					if last_point not in points:
						points[last_point] = "sas2"
					next = points[last_point]
					neighb_item = f"element{self.elements[item][next]}"
					
				next, item, nr = self.next_element(neighb_item, nr)
					
		except BreakFunc:
			pass
			# print("End of searching flank prot")
	
	def next_element(self, neighb, nr):
		'''przejście do kolejnego elementu'''
		next = self.check_element_dir(neighb, nr)
		nr = self.elements[neighb]["nr"]
		item = f"element{nr}"
		return next, item, nr
	
	def flank_end(self, item, points, last_point):
		points = self.check_last_point(points, last_point)
		if not points:
			raise BreakFunc
		nr = self.elements[item]["nr"]
		return nr, f"element{nr}", points

	def check_element_dir(self, neighbour, nr):
		'''sprawdza czy sąsiedni element nie wskazuje na poprzedni, zwraca sąsiada'''
		if self.elements[neighbour]["sas2"] == nr or \
			self.elements[neighbour]["sas3"] == nr:
			return "sas1"
		return "sas2"
		
	def check_last_point(self, switches, last_switch):
		if any(switches):
			if switches[last_switch] == "sas2":
				switches[last_switch] = "sas3"
			else:
				if all(i == "sas3" for i in switches.values()):
					switches = {}
				else:
					switches.pop(last_switch)
		return switches

