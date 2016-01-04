import csv
import yaml
import io
import re
import textwrap
from collections import OrderedDict

def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))
    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

yaml.add_representer(OrderedDict, represent_ordereddict)

def to_level(lvl):
     return 0 if lvl == "Cantrip" else int(lvl)

def to_duration(dur):
    concentration = True if re.match(".*[Cc]oncentration.*", dur) else False
    dur = re.sub("Concentration, (.*)", "C: \\1", dur)
    dur = re.sub("up to (.*)", "\\1 max", dur)
    dur = re.sub("minutes?", "min", dur)
    dur = re.sub("hour", "hr", dur)
    dur = re.sub("Instantaneous", "Inst.", dur)
    return dur, concentration

def to_description_lines(desc, len=80):
    lines = textwrap.wrap(desc, len)
    desc_lines = ["  %s" % s.strip() for s in lines]
    return desc_lines

def to_description(desc, len=80):
    return desc
    # desc_lines = to_description_lines(desc, len)
    # delim = "\n"
    # out = ">\n" + delim.join(desc_lines) + "\n"
    # return out

with io.open("../data/spell_list.yaml", "wb") as spellfile:
    with io.open("../data/spell_list.csv", "rb") as csvfile:
        r = [row for row in csv.reader(csvfile.read().splitlines())]
        for row in r:
          name = row[0]
          level = to_level(row[1])
          ritual = (row[2] != "")
          school = row[3]
          casting_time = row[4]
          range = row[5]
          components = row[6]
          materials = row[7]
          duration, concentration = to_duration(row[8])
          save = ""
          damage = ""
          damage_type = ""
          ref = "PHB 999"
          description = to_description(row[19])
          print "description: " + description

          data = OrderedDict([(name, OrderedDict([
              ("level", level),
              ("ritual", ritual),
              ("school", school),
              ("casting_time", casting_time),
              ("range", range),
              ("components", components),
              ("materials", materials),
              ("duration", duration),
              ("save", save),
              ("damage", damage),
              ("damage_type", damage_type),
              ("concentration", concentration),
              ("ref", ref),
              ("description", description)
          ]))])
          spellfile.write(yaml.dump(data, default_flow_style=False))
