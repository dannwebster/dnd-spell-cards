__author__ = 'dannwebster'

import os
import shutil
from os.path import join, dirname
import io
import yaml
from collections import OrderedDict, defaultdict
from genshi.template import MarkupTemplate, TemplateLoader

def yaml_to_dict(path):
    with io.open(path, "r") as stream:
        data = yaml.safe_load(stream)
    return data

class Spell:
    """
    a single spell
    """
    def __init__(self, name, data):
        self.name = name
        self.__dict__.update(data)
        self.school_level = self._create_school_level_()

    def _create_school_level_(self):
        level = self.level
        suffix = "st" if level == 1 else "nd" if level == 2 else "rd" if level == 3 else "th"
        return "%s%s-level %s" % (self.level, suffix, self.school) if self.level > 0 else self.school + " Cantrip"

    def __str__(self):
        return """
        %s
        %s
        Casting Time: %s
        Range: %s
        Components: %s
        %s
        """ % (self.name, self.school_level, self.casting_time,
               self.range, self.components, self.description)

class CharacterSpell(Spell):
    def __init__(self, spell, spell_class_name, spell_class_data, is_preferred, notes):
        self.spell_class = spell_class_name
        self.notes = ""
        self.spell_ability = spell_class_data["ability"]
        self.save_dc = spell_class_data["save_dc"]
        self.attack_bonus = spell_class_data["attack_bonus"]
        self.damage_bonus = spell_class_data["damage_bonus"]
        self.name = spell.name
        self.level = spell.level
        self.school = spell.school
        self.school_level = spell.school_level
        self.casting_time = spell.casting_time
        self.ritual = spell.ritual
        self.concentration = spell.concentration
        self.range = spell.range
        self.components = spell.components
        self.duration = spell.duration
        self.ref = spell.ref
        self.materials = spell.materials if hasattr(spell, "materials") else None
        self.description = spell.description
        self.damage = spell.damage if spell.damage else None
        self.damage_type = spell.damage_type if spell.damage_type else None
        self.save = spell.save if spell.save else None
        self.is_preferred = is_preferred
        self.has_attack = self.damage is not None
        self.has_save = self.save is not None
        self.notes = notes

    def __str__(self):
        return self.spell_class + "Spell:\n"

    def save_desc(self):
        return "%s: DC %s" % (self.save, self.save_dc) if self.has_save else "N/A"

    def damage_desc(self):
        return "%s%s %s" % (self.damage, self.damage_bonus_desc(), self.damage_type) if self.has_attack else "N/A"

    def damage_bonus_desc(self):
        return self.pos_neg(self.damage_bonus)

    def attack_bonus_desc(self):
        if self.has_attack:
            return self.pos_neg(self.attack_bonus)
        else:
            return "N/A"

    def type_desc(self):
        return "%s" % (self.school_level)

    def level_icon(self):
        return "%s.svg" % self.level

    def school_icon(self):
        return self.school.lower() + ".png"

    def pos_neg(self, value):
        return "+%s" % value if value >= 0 else "%s" % value

    def __str__(self):
        return """
        %s
        %s
        Casting Time: %s
        Range: %s
        Components: %s (%s)
        %s
        """ % (self.name, self.school_level, self.casting_time,
               self.range, self.components, self.materials, self.description)
class Character:
    """
    All the info for a specific character
    """
    def __init__(self, spellbook, class_spell_lists, path):
        data = yaml_to_dict(path)
        self.__dict__.update(data)
        self.by_name = OrderedDict()
        self.by_level = defaultdict(list)
        self.preferred = set(self.preferred)
        self.image_name = os.path.basename(self.image)
        for spell_class_name in self.spell_classes:
            spell_class_data = self.spell_classes[spell_class_name]
            character_class_spell_list = class_spell_lists.get_spells(spell_class_name, spell_class_data["level"])

            for cantrip_name in spell_class_data["cantrips"]:
                self.add_spell(spellbook, cantrip_name, spell_class_name, spell_class_data)

            for spell_name in character_class_spell_list:
                self.add_spell(spellbook, spell_name, spell_class_name, spell_class_data)

            for special_name in spell_class_data["special"]:
                self.add_spell(spellbook, special_name, spell_class_name, spell_class_data)

    def get_notes(self, spell_name):
        return self.notes.get(spell_name) if self.notes is not None else None

    def add_spell(self, spellbook, spell_name, spell_class_name, spell_class_data):
        spell = spellbook.get_spell(spell_name)
        if spell != None:
            is_preferred = spell_name in self.preferred
            notes = self.get_notes(spell_name)
            character_spell = CharacterSpell(spell, spell_class_name, spell_class_data, is_preferred, notes)
            self.by_name[spell_name.upper()] = character_spell
            self.by_level[spell.level].append(character_spell)

    def __str__(self):
        return """
        Owner: %s
        Name: %s
        Image: %s
        Spells: %s
        """ % (self.owner, self.name, self.image, self.by_name)

class SpellBook:
    """
    All the spells from the spell book
    """
    def __init__(self, path):
        data = yaml_to_dict(path)
        self._by_name = {}
        self._by_level = defaultdict(list)
        for spell_name in data:
            spell_data = data[spell_name]
            spell = Spell(spell_name, spell_data)
            self._by_name[spell_name.lower()] = spell
            self._by_level[spell.level].append(spell)

    def get_spell(self, spell_name):
        return self._by_name.get(spell_name.lower())

class ClassSpellLists:
    """
    All the spells for a given class
    """
    def __init__(self, path):
        self.data = yaml_to_dict(path)

    def get_spells(self, character_class, level):
        level_list = self.data[character_class]
        spells = []
        for level in range(1, level+1):
            level_spells = level_list[level]
            spells.extend(level_spells)
        return spells


class Grimoire:
    def __init__(self, character, template_dir, template_file):
        self.character = character
        self.template_dir = template_dir
        self.template_file = template_file

    def to_html(self, image_dir, output_base_dir, cards_per_row):
        output_dir = join(output_base_dir, self.character_output_dir())
        char_img_dir = join(output_dir, "images")

        self.move_icon_images(image_dir, char_img_dir)
        self.move_character_image(char_img_dir)
        self.write_index_file(output_dir, cards_per_row)


    def character_output_dir(self):
        return self.character.character_name.lower().replace(" ", "_") + "_spells"

    def write_index_file(self, output_dir, cards_per_row):
        loader = TemplateLoader(self.template_dir)
        template = loader.load(self.template_file)

        stream = template.generate(character=self.character, cards_per_row=cards_per_row, util=TemplateUtil())
        html = stream.render('xhtml')

        index_file = join(output_dir, "index.html")
        with io.open(index_file, "w") as file:
            file.write(html)

    def move_icon_images(self, image_dir, char_img_dir):
        shutil.rmtree(char_img_dir, ignore_errors=True)
        shutil.copytree(image_dir, char_img_dir)

    def move_character_image(self, img_dir):
        shutil.copy(self.character.image, img_dir)

class TemplateUtil:
    def group(self, cells, columns_per_row, rows_per_page):
        """Group an iterable into an n-tuples iterable. Incomplete tuples
        are discarded e.g.

        >>> list(group(range(10), 3))
        [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, None, None)]
        """
        return map(None, *[iter(cells)] * columns_per_row)

