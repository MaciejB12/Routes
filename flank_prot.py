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
			# with open(filename, "r") as f: for YAML
			#	elements_file = load(f)
			with open(filename, "r") as f: # for JSON
				elements_file = json.load(f)
		except ScannerError as e:
			print(f"YAML SCANNER ERROR: {e}")
		except json.JSONDecodeError as e:
			print(f"JSON decode error: {e}")

		self.elements = elements_file["routes"]
		self.ort = ort
		self.route = OrderedDict()
		self.route_list = list()
	
	def search_overlap(self, neighbour):
		'''szuka drogi ochronnej (nast. el. za sem. koncowym drogi przebiegu)'''
		print(f"{self.elements[neighbour]['name']} w drodze ochronnej")
	
	def set_pos(self, pos):
		if pos == "N":
			return "P"
		return "N"
	
	def check_flank(self, item, op_pos, nxt):
		# czy element jest semaforem skierowanym w dobrą stronę - może dawać ochr. boczną
		if self.elements[item]["type"] == "signal" and nxt == "sas1":
			return 1
		# czy element jest zwr skierowaną w dobrą stronę - może dawać ochr. boczną
		elif self.elements[item]["type"] == "switch" and \
			self.elements[item]["orientation"] == op_pos:
			return 1
		# czy element jest końcem toru - nie może dawać ochrony bocznej - kończy wyszukiwanie ochr. bocznej
		elif self.elements[item]["type"] == "eot":
			return 2

	def search_flank_prot(self, start_item, start_next):
		pos = self.elements[start_item]["orientation"]
		nr = self.elements[start_item]["nr"]
		nxt, item = start_next, start_item
		points, last_point = {}, {}
		op_pos = self.set_pos(pos)		
		try:
			while True:
				neighb_item = f"element{self.elements[item][nxt]}"
				if self.check_flank(item, op_pos, nxt) == 1:	
					self.route[self.elements[item]['name']] = "ob"
					item = self.flank_end(start_item, points, last_point)
					neighb_item = f"element{self.elements[item][start_next]}"			
				elif self.check_flank(item, op_pos, nxt) == 2:
					item = self.flank_end(start_item, points, last_point)
					neighb_item = f"element{self.elements[item][start_next]}"
				else:
					pass # w tym przypadku to nie jest el. dający ochr. boczną
				# zwr kierunkowa w ścieżce szukania ochr. bocznej
				if self.elements[item]["type"] == "switch" and \
					self.elements[item]["orientation"] == pos and \
					item != start_item:
					last_point = self.elements[item]["name"]

					nxt = self.check_point(points, last_point)
					neighb_item = f"element{self.elements[item][nxt]}"
					
				nxt, nr, item = self.next_element(neighb_item, nr)
		except BreakFunc:
			pass # koniec szukania ochrony bocznej
	
	def check_point(self, points, last_point):
		'''sprawdza czy zwrotnica jest w liście'''
		if last_point not in points:
			points[last_point] = "sas2" # kier. szuk. drogi przeb.
		return points[last_point]
	
	def next_element(self, neighb, nr):
		'''przejście do kolejnego elementu'''
		nxt = self.check_element_dir(neighb, nr)
		nr = self.elements[neighb]["nr"]
		item = f"element{nr}"
		return nxt, nr, item
	
	def flank_end(self, item, points, last_point):
		'''sprawdza ost. zwrotnice w ochronie bocznej, ustawia sąsiedni element dla
		nowej scieżki szukania drogi ochronnej'''
		points = self.check_last_point(points, last_point)
		if not points:
			raise BreakFunc
		nr = self.elements[item]["nr"]
		return f"element{nr}"

	def check_element_dir(self, neighbour, nr):
		'''sprawdza czy sąsiedni element nie wskazuje na poprzedni, zwraca sąsiada'''
		if self.elements[neighbour]["sas2"] == nr or \
			self.elements[neighbour]["sas3"] == nr:
			return "sas1"
		return "sas2"
		
	def check_last_point(self, switches, last_switch):
		'''sprawdza ost. zwrotnicę na liście'''
		if any(switches):
			if switches[last_switch] == "sas2":
				switches[last_switch] = "sas3"
			else:
				if all(i == "sas3" for i in switches.values()):
					switches = {}
				else:
					switches.pop(last_switch)
		return switches

