#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main - uruchamia program wyszukiwania przebiegów
# WYKONAWCA: MB
# UTWORZONY: 04-07-2018
# NAZWA: routes_main.py

from routes_class import Routes

filename = "routes3.json"
routes = Routes(filename, "P")

try:
	for element in routes.elements:
		e = routes.elements[element]
		type = e["type"]
		try:
			orientation = e["orientation"]
			if type == "signal" and orientation == routes.orientation:
				routes.search_elements(element, orientation)
		except KeyError as error:
			# print(f"No key {error} in element {element}")
			continue	
except FileNotFoundError as error:
	print(f"No JSON file: {error}")