#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main - uruchamia program wyszukiwania przebiegów dla JSON
# WYKONAWCA: MB
# UTWORZONY: 29-11-2018
# NAZWA: routes_main_json.py

from routes_class import Routes

import json

filename = "routes3.json"
rs = Routes(filename, "N")

try:
	for element in rs.elms: # elms = elms_file["routes"]
		e = rs.elms[element]
		_type = e["type"]
		try:
			ort = e["orientation"]
			if _type == "signal" and ort == rs.ort:
				rs.search_elements(element, ort)
		except KeyError as error:
			# print(f"No key {error} in element {element}")
			continue	
except FileNotFoundError as error:
	print(f"No JSON file: {error}")