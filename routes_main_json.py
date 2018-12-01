#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main - uruchamia program wyszukiwania przebiegów dla JSON
# WYKONAWCA: MB
# UTWORZONY: 29-11-2018
# NAZWA: routes_main_json.py

filename = "routes4.json"
routes = Routes(filename, "N")

try:
	for element in routes.elements: # elements = elements_file["routes"]
		e = routes.elements[element]
		type = e["type"]
		try:
			orientation = e["orientation"]
			if type == "signal" and orientation == routes.orientation:
				routes.search_elements(element, orientation)
		except KeyError as error:
			print(f"No key {error} in element {element}")
			continue	
except FileNotFoundError as error:
	print(f"No JSON file: {error}")