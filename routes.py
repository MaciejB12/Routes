#!/usr/bin/env python
# -*- coding: utf-8 -*-
# wyszukuje dostępne przebiegi na podstawie elementów w pliku json
# WYKONAWCA: MB
# UTWORZONY: 13-06-2018
# NAZWA: routes.py

import json
	
def search_el(element, position):
	'''przeszukuje jsona'''
	name = routes[element]["name"] # nazwa, numer, opis elementu
	nr = routes[element]["nr"]
	item = f"element{nr}"
	next = "sas2" # zaczynamy zawsze od sąsiada od strony nr 2
	switches = {} # pusty słownik dla zwrotnic wraz z położneniami
	last_switch = "" # ostatnia zwrotnica w przebiegu
	print("\nRoute: ", end="")
	
	while True:
		# wydrukuj element
		print(f"{routes[item]['name']} ", end="")
		# ustaw sąsiedni element
		neighb_item = f"element{routes[item][next]}"
		
		# sprawdzamy czy element jest końcem drogi przebiegu (semafor)
		if routes[item]["type"] == "signal" and \
			routes[item]["name"] != name and routes[item]["position"] == position: # position = położenie zwrotki (z ostrza lub na ostrze)
			
			# zamknąć to w funkcje?
			switches = check_last_point(switches, last_switch) # sprawdzamy akt. położenie ost. zwrotnicy
			if not switches: # jeżeli zwraca pusty słownika to przerwij pętle
				break
			next, nr, item = set_next_element(element)   # jeśli koniec przebiegu to zacznij znowu od pierwszego elementu
			neighb_item = f"element{routes[item][next]}" # zwraca numer nast. elementu
			print(f"\nRoute: {routes[item]['name']} ", end="")

		# sprawdzamy czy element jest końcem drogi przebiegu	
		elif routes[item]["type"] == "li": # iface do blokady
			
			# zamknąć to w funkcje?
			switches = check_last_point(switches, last_switch) # sprawdzamy akt. położenie ost. zwrotnicy
			if not switches:
				break
			next, nr, item = set_next_element(element)   # jeśli koniec przebiegu to zacznij znowu od pierwszego elementu
			neighb_item = f"element{routes[item][next]}" # zwraca numer nast. elementu
			print(f"\nRoute: {routes[item]['name']} ", end="")

		# sprawdzamy czy zwrotnica jest już uwzględniona w słowniku
		if routes[item]["type"] == "switch" and routes[item]["position"] == position:
			last_switch = routes[item]["name"]
			if last_switch not in switches: # jeżeli nie ma w słowniku to dodaj z pozycją na wprost
				switches[last_switch] = "sas2"
			next = switches[last_switch] # wybór położenia zwrotnicy kierunkowej
			neighb_item = f"element{routes[item][next]}" # wybór sąsiedniego elementu (ewent. nadpisuje sas3 zamiast sas2 ust. na pocz.)
			# print("NEIGHB_ITEM_SW", neighb_item, next)
		
		# sprawdzamy czy sąsiedni element nie wskazuje na poprzedni
		next = check_element_direction(neighb_item, nr)
		
		# skok do sąsiedniego elementu
		nr = routes[neighb_item]["nr"]
		item = f"element{nr}"

def check_element_direction(neighbour, nr):
	'''sprawdza czy sąsiedni element nie wskazuje na poprzedni, zwraca sąsiada'''
	if routes[neighbour]["sas2"] == nr or \
		routes[neighbour]["sas3"] == nr:
		return "sas1"
	else:
		return "sas2"
		
def set_next_element(el):
	'''ustawia sąsiedni element'''
	nr = routes[el]["nr"]
	# item = f"element{nr}"
	# return f"element{routes[item][next]}"
	return "sas2", routes[el]["nr"], f"element{nr}" 
	
def check_last_point(switches, last_switch):
	'''sprawdza czy jest jakaś zwrotnica w przebiegu i aktualne położenie ostatniej zwrotnicy w przebiegu'''
	if any(switches):
		if switches[last_switch] == "sas2": # jeżeli ost. zwrotnica jest na wprost to ustaw ją na bok
			switches[last_switch] = "sas3"
		else:
			if all(i == "sas3" for i in switches.values()): # w przeciwnym przypadku jeżeli wszystkie są na bok to je usuń
				switches = {}
			else:
				switches.pop(last_switch) # usuń ostatnią jeżeli jest na bok
	return switches

# MAIN
	
try:
	p = "P"
	with open("routes.json", "r") as f:
		el_file = json.load(f)
	routes = el_file["routes"]
	for route in routes:
		type = routes[route]["type"]
		try:
			position = routes[route]["position"]
			if type == "signal" and position == p:
				search_el(route, position)
		except KeyError as error:
			# print(f"KEY ERROR: {error}")
			continue
except FileNotFoundError as error:
	print(f"BRAK PLIKU JSON: {error}")




	
	
	
	