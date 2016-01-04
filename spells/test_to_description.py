from unittest import TestCase

from csv_to_yaml import to_description, to_description_lines
from spells import TemplateUtil

class TestSpellFunctions(TestCase):

    def test_to_description_lines(self):
        lines = to_description_lines("this is a lot of lines long", 5)
        self.assertEqual("  this", lines[0])
        self.assertEqual("  is a", lines[1])
        self.assertEqual("  lot", lines[2])

    def test_to_description(self):
        desc = to_description("this is a lot of lines long", 5)
        self.assertEqual( " >\n"
                          "  this\n"
                          "  is a\n"
                          "  lot\n"
                          "  of\n"
                          "  lines\n"
                          "  long\n", desc)

    def test_group(self):

        # given
        cells = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        subject = TemplateUtil()

        pages = subject.group(cells, 2, 3)
        self.assertEqual(2, len(pages))
        page_1_rows = pages[0]
        page_2_rows = pages[1]

        self.assertEqual(3, len(page_1_rows))
        self.assertEqual(2, len(page_2_rows))

