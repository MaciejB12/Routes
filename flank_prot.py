#!/usr/bin/env python
# -*- coding: utf-8 -*-
# moduł wyszukiwania ochrony bocznej i drogi ochronnej
# WYKONAWCA: MB
# UTWORZONY: 09-07-2018
# NAZWA: flank_prot.py

import json
from yaml import load
from yaml.scanner import ScannerError
from collections import OrderedDict

class BreakFunc(Exception): pass

class FlankProt:
	
	def __init__(self, filename, ort):
		try:
			with open(filename) as f: # for YAML elms
				elms_file = load(f)
			# with open(filename) as f: # for JSON elms
			#	elms_file = json.load(f)
		except ScannerError as e:
			print(f"YAML SCANNER ERROR: {e}")
		except json.JSONDecodeError as e:
			print(f"JSON decode error: {e}")

		self.elms = elms_file["routes"]
		self.ort = ort
		self.route_list, self.drs_list = [], []
		self.n = 2
	
	def search_overlap(self, neighbour):
		'''szuka drogi ochronnej (nast. el. za sem. koncowym drogi przebiegu)'''
		print(f"{self.elms[neighbour]['name']} w drodze ochronnej")
	
	def set_pos(self, pos):
		if pos == "N":
			return "P"
		return "N"
	
	def check_flank(self, item, op_pos, nxt):
		# czy element jest semaforem skierowanym w dobrą stronę - może dawać ochr. boczną
		if self.elms[item]["type"] == "signal" or \
			self.elms[item]["type"] == "sh_signal" and nxt == "sas1":
			return 1
		# czy element jest zwr skierowaną w dobrą stronę - może dawać ochr. boczną
		elif self.elms[item]["type"] == "switch" and \
			self.elms[item]["orientation"] == op_pos:
			return 1
		# czy element jest końcem toru - nie może dawać ochrony bocznej - kończy wyszukiwanie ochr. bocznej
		elif self.elms[item]["type"] == "eot":
			return 2

	def search_flank_prot(self, start_item, start_next):
		pos = self.elms[start_item]["orientation"]
		nr = self.elms[start_item]["nr"]
		nxt, item = start_next, start_item
		last_point, points = "", OrderedDict()
		op_pos = self.set_pos(pos)		
		try:
			while True:
				neighb_item = f"element{self.elms[item][nxt]}"
				if self.check_flank(item, op_pos, nxt) == 1:	
					# self.route[self.elms[item]['name']] = "ob"
					self.route_list.append((self.elms[item]['name'], "ob"))
					item = self.flank_end(start_item, points, last_point)
					neighb_item = f"element{self.elms[item][start_next]}"			
				elif self.check_flank(item, op_pos, nxt) == 2:
					item = self.flank_end(start_item, points, last_point) # powtórzenia !
					neighb_item = f"element{self.elms[item][start_next]}" # powtózenia !
				else:
					pass # w tym przypadku to nie jest el. dający ochr. boczną
				# zwr kierunkowa w ścieżce szukania ochr. bocznej
				if self.elms[item]["type"] == "switch" and \
					self.elms[item]["orientation"] == pos and \
					item != start_item:
					last_point = self.elms[item]["name"]
					nxt = self.check_point(points, last_point)
					neighb_item = f"element{self.elms[item][nxt]}"
				# nastawienie zwr w ochr bocznej - do modyfikacji
				if self.elms[neighb_item]["type"] == "switch" and \
					self.elms[neighb_item]["orientation"] == op_pos:
					z = self.set_flank_prot_point(neighb_item, nr)
					# self.drs[self.elms[neighb_item]["name"]] = z
					self.drs_list.append((self.elms[neighb_item]["name"], z))
					# print(f"kier zwr {self.elms[neighb_item]['name']} w ochr bocz: {z} {op_pos}")
				
				nxt, nr, item = self.next_element(neighb_item, nr)
				# print(f"SEC nxt: {nxt}, nr: {nr}, item: {item}, neighb: {neighb_item}\n")
		except BreakFunc:
			# print(f"\nkoniec szukania ochrony bocznej, wybrano item: {item}")
			pass # koniec szukania ochrony bocznej
	
	def check_point(self, points, last_point):
		'''sprawdza czy zwrotnica jest w liście'''
		# else dodane ze względu nie niewłaściwe przypisywanie
		# sąsiednich el. na zwrotnicy przejeżdżanej na ostrze
		if last_point not in points:
			points[last_point] = "sas2" # kier. szuk. drogi przeb.
		# else:
		#	points[last_point] = "sas3"
		return points[last_point]
	
	def next_element(self, neighb, nr):
		'''przejście do kolejnego elementu'''
		
		nxt = self.check_element_dir(neighb, nr)
		nr = self.elms[neighb]["nr"]
		item = f"element{nr}"
		return nxt, nr, item
	
	def flank_end(self, item, points, last_point):
		'''sprawdza ost. zwrotnice w ochronie bocznej, ustawia sąsiedni element dla
		nowej scieżki szukania drogi ochronnej'''
		points = self.check_last_point(points, last_point)
		if not points:
			raise BreakFunc
		nr = self.elms[item]["nr"]
		return f"element{nr}"

	def check_element_dir(self, neighbour, nr):
		'''sprawdza czy sąsiedni element nie wskazuje na poprzedni, zwraca sąsiada'''
		if self.elms[neighbour]["sas2"] == nr or \
			self.elms[neighbour]["sas3"] == nr:
			return "sas1"
		return "sas2"

	def set_flank_prot_point(self, neighbour, nr):
		'''ustawia zwrotnicę w ochronie bocznej'''
		if self.elms[neighbour]["sas2"] == nr:
			return "sas3"
		elif self.elms[neighbour]["sas3"] == nr:
			return "sas2"
		
	def check_last_point(self, points, last_point):
		'''sprawdza ost. zwrotnicę na liście'''
		# else zmienione ze względu na niewłaściwe przypisywanie
		# sąsiednich el. na zwrotnicy przejeżdżanej na ostrze
		if any(points):
			# if points[last_point] == "sas2":
			#	points[last_point] = "sas3"
			# else:
			
			for k in list(reversed(points.keys())):
				# print(points)
				if points[k] == "sas3":
					del points[k]
					# print(f"points del {points}")
				else:
					points[k] = "sas3"
					return points
				# if all(i == "sas3" for i in switches.values()):
					# switches = {}
				# else:
					# switches.pop(last_switch)
		# print(f"points inside func {points}")
		# return points

