#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main - uruchamia program wyszukiwania przebiegów dla YAML
# WYKONAWCA: MB
# UTWORZONY: 04-07-2018
# NAZWA: routes_main.py

from routes_class import Routes

from yaml import load
from yaml import YAMLError

fn = "routes3.yml" # z sys.argv pobierać
rs = Routes(fn, "P")

try:
	for el in rs.elements:
		e = rs.elements[el]
		type = e["type"]
		try:
			ort = e["orientation"]
			if type == "signal" and ort == rs.ort:
				rs.search_elements(el, ort)
		except KeyError as err:
			# print(f"Key error: {err}")
			continue
		except YAMLError as err:
			print(f"Yaml error: {err}")
			

except FileNotFoundError as err:
	print(f"No YML file: {err}")
