#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main - uruchamia program wyszukiwania przebiegów dla JSON
# WYKONAWCA: MB
# UTWORZONY: 29-11-2018
# NAZWA: routes_main_json.py

from routes_class import Routes

import json

filename = "routes4.json"
routes = Routes(filename, "P")

try:
	for element in routes.elements: # elements = elements_file["routes"]
		e = routes.elements[element]
		type = e["type"]
		try:
			ort = e["orientation"]
			if type == "signal" and ort == routes.ort:
				routes.search_elements(element, ort)
		except KeyError as error:
			# print(f"No key {error} in element {element}")
			continue	
except FileNotFoundError as error:
	print(f"No JSON file: {error}")