#!/usr/bin/env python3
"""Generates entities.h and entities.c using entities.json from https://html.spec.whatwg.org/entities.json

Delete entities.json if you want to fetch the latest version.
The current version has 1 and 2 codepoint entities.
If the spec is updated to include 3 or more codepoints per entity, then this script along with
gdImageStringFTEx and gd_Entity_To_Unicode (from gdft.c) will need to be modified.
A warning is issued for any such entities found and only the first 2 codepoints are used.
"""

import json
import os
import os.path
import re
import urllib.request
from pathlib import Path

__author__ = "Sterling Pickens"
__copyright__ = "Copyright 2021, The libgd Project"
__credits__ = ["Sterling Pickens", "Mike Frysinger"]
__license__ = "MIT; see the COPYING file"
__version__ = "1.0.0"
__maintainer__ = "Sterling Pickens"
__email__ = "sterling_pickens@yahoo.com"
__status__ = "Production"

# Ensure we are only in src dir
SRCDIR = Path(__file__).resolve().parent
os.chdir(SRCDIR)

# Declare File content strings
C_FILE_HEAD = """/*
 * Generated file - do not edit directly.
 * This file was generated from:
 *     https://html.spec.whatwg.org/entities.json
 * by means of entities.py in the libgd src dir
 */

#include "entities.h"

const struct gd_entities_s gd_entities[NR_OF_ENTITIES] = {
"""
H_FILE_HEAD = """/*
 * Generated file - do not edit directly.
 * This file was generated from:
 *     https://html.spec.whatwg.org/entities.json
 * by means of entities.py in the libgd src dir
 */

#ifndef GD_ENTITIES_H
#define GD_ENTITIES_H 1

#include <stdlib.h>
#include <stdint.h>

// html entity strings are entity prefix + string + suffix limited
// hex and dec should be limited to current unicode spec + entity prefix + suffix

#define ENTITY_HEX_LENGTH_MAX 10
#define ENTITY_DEC_LENGTH_MAX 10
"""
H_FILE_TAIL = """
extern const struct gd_entities_s gd_entities[NR_OF_ENTITIES];

#endif
"""

# Check for entities.json and fetch if needed
if not os.path.exists("entities.json"):
    print("entities.json not found, attempting to download...")
    with open("entities.json", "wb") as file_json:
        file_json.write(urllib.request.urlopen("https://html.spec.whatwg.org/entities.json").read())
        print("\tsuccessful")

# Load json obj
with open("entities.json", "rb") as file_json:
    entities = json.load(file_json)
name_matcher = re.compile(r"&\S+;")

# Sum of total matching entities
total_entities = sum(bool(name_matcher.match(key)) for key in entities)

# Find longest entity
len_name_max = max(len(key) for key in entities if name_matcher.match(key))

# Write entities.h file
with open("entities.h", mode="w") as file_ent_h:
    file_ent_h.write(H_FILE_HEAD)
    file_ent_h.write(f"#define NR_OF_ENTITIES {total_entities}\n");
    file_ent_h.write(f"#define ENTITY_NAME_LENGTH_MAX {len_name_max}\n\n");
    file_ent_h.write("struct gd_entities_s {\n\tconst char *name;\n\tuint32_t codepoint1;\n\tuint32_t codepoint2;\n};\n");
    file_ent_h.write(H_FILE_TAIL)

# Write entities.c file
with open("entities.c", mode="w") as file_ent_c:
    file_ent_c.write(C_FILE_HEAD)
    # Write json entities to struct
    for key in entities:
        if name_matcher.match(key):
            string = "\t" + "{\"" + key.replace("&", "").replace(";", "") + "\", "
            codepoints = entities[key]["codepoints"]
            string = string + str(codepoints[0]) + ", "
            if len(codepoints) > 1:
                string = string + str(codepoints[1]) + "}"
            else:
                string = string + "0}"
            if len(codepoints) > 2:
                print("Warning: entity with >2 codepoints detected")
            file_ent_c.write(string + ",\n")
    # Write file end
    file_ent_c.write("};\n")

# Print Summary
print("entities.h & entities.c updated from entities.json")
print(f"\tTotal entities: {total_entities}\n\tLongest entity: {len_name_max}")
