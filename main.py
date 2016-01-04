from spells import Spell, SpellBook, Grimoire, ClassSpellLists, TemplateUtil, Character
from os.path import join, dirname
import io

DIR=dirname(__file__)

DATA_DIR=join(DIR, "data")
TEMPLATE_DIR=join(DIR, "templates")
CHARACTERS_DIR=join(DIR, "characters")
IMAGE_DIR=join(DIR, "images")

TEMPLATE_FILE="spell_cards.html"
SPELL_BOOK_FILE="spell_list.yaml"
CLASS_SPELL_LISTS_FILE="class_spell_lists.yaml"

# Runtime Parameters
OUTPUT_DIR="/tmp"
CHARACTER_FILE= "ayonga_lionsblood.yaml"

CARDS_PER_ROW=4

SPELL_BOOK_PATH=join(DATA_DIR, SPELL_BOOK_FILE)
CLASS_SPELL_LISTS_DIR=join(DATA_DIR, CLASS_SPELL_LISTS_FILE)
CHARACTER_PATH=join(CHARACTERS_DIR, CHARACTER_FILE)

class_spell_lists = ClassSpellLists(CLASS_SPELL_LISTS_DIR)
spellbook = SpellBook(SPELL_BOOK_PATH)
character = Character(spellbook, class_spell_lists, CHARACTER_PATH)
grimoire = Grimoire(character, TEMPLATE_DIR, TEMPLATE_FILE)

grimoire.to_html(IMAGE_DIR, OUTPUT_DIR, CARDS_PER_ROW)
