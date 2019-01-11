#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main - uruchamia program wyszukiwania przebiegów dla YAML
# WYKONAWCA: MB
# UTWORZONY: 04-07-2018
# NAZWA: routes_main.py

from routes_class import Routes

import sys
from yaml import load
from yaml import YAMLError

try:
	conf = sys.argv[1]
except IndexError as err:
	print(f"{err} : no arg")
	sys.exit()

fn = "routes6.yml" # z sys.argv pobierać
rs = Routes(fn, conf, "N")

try:
	for el in rs.elms:
		e = rs.elms[el]
		type = e["type"]
		try:
			ort = e["direct"]
			if type == "signal" and ort == rs.ort:
				rs.search_elements(el, ort)
		except KeyError as err:
			# print(f"Key error: {err}")
			continue
		except YAMLError as err:
			print(f"Yaml error: {err}")
except FileNotFoundError as err:
	print(f"No YML file: {err}")
