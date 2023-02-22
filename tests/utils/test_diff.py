# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Author: Mauro Soria

from unittest import TestCase

import requests
from bs4 import BeautifulSoup

from lib.utils.diff import DynamicContentDiffer, get_elements_differ_ratio, generate_matching_regex




class TestDiff(TestCase):
    def test_generate_matching_regex(self):
        self.assertEqual(generate_matching_regex("add.php", "abc.php"), "^a.*\\.php$", "Matching regex isn't correct")

    def test_get_element_ratio(self):
        element = """
        <div class="section" id="beautiful-soup-documentation-{id}">
            <span id="documentation-{id}"></span>
            <h1>
                Beautiful Soup Documentation <a class="headerlink" href="#beautiful-soup-documentation" 
                title="Permalink to this headline">*</a>
            </h1>
        </div>
        """

        base_html = element.format(id=1)
        test_html = element.format(id=2)

        # Test with base element
        base_element = BeautifulSoup(base_html, "html.parser").find("div")
        ratio = get_elements_differ_ratio(base_element, base_element)
        self.assertEqual(ratio, 1.0, "Base element should be 100% similar to itself")

        # Test with almost same elements
        test_element = BeautifulSoup(test_html, "html.parser").find("div")
        ratio = get_elements_differ_ratio(base_element, test_element)
        self.assertGreater(ratio, 0.98, "Element's ratio to similar element should be greater than 98")

        # Test with different elements
        different_html = test_html.replace("Beautiful", "Ugly").replace("div", "another_tag")
        test_element = BeautifulSoup(different_html, "html.parser").find("another_tag")
        ratio = get_elements_differ_ratio(base_element, test_element)
        self.assertLess(ratio, 0.5, "Element's ratio to different element should be less than 95")

    def test_dynamic_content_differ(self):
        base_page = requests.get("https://python.org").text
        differ = DynamicContentDiffer(base_page)

        # Test with same page
        result = differ.compare_to(base_page)
        self.assertTrue(result, "Page should be similar to itself")

        # Test with almost same page
        test_page = requests.get("https://python.org").text
        result = differ.compare_to(test_page)
        self.assertTrue(result, "Page should be almost similar to itself")

        # # Test with different page
        test_page = requests.get("https://www.google.com/").text
        result = differ.compare_to(test_page)
        self.assertFalse(result, "Page should be different to another page")
