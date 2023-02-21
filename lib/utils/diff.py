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

import difflib
import re

from bs4 import BeautifulSoup

from lib.core.settings import MAX_MATCH_RATIO


def get_element_ratio(base_tag, test_tag):
    """
    Go through the base response and count all elements diff ratio.
    """
    text_score = difflib.SequenceMatcher(None, base_tag.text, test_tag.text).quick_ratio()
    name_score = difflib.SequenceMatcher(None, base_tag.name, test_tag.name).quick_ratio()
    children_score = difflib.SequenceMatcher(None,
                                             [child.name for child in base_tag.children],
                                             [child.name for child in test_tag.children]).quick_ratio()

    if not base_tag.attrs and not test_tag.attrs:
        attrs_score = 1
    else:
        attrs_score = 0
        for key in base_tag.attrs.keys():
            if key in test_tag.attrs.keys():
                attr_score = difflib.SequenceMatcher(None, base_tag.attrs[key], test_tag.attrs[key]).quick_ratio()
                attrs_score += attr_score
        for key in test_tag.attrs.keys():
            if key not in base_tag.attrs.keys():
                attrs_score -= 1
            attrs_score = 0 if attrs_score < 0 else attrs_score
        attrs_score = attrs_score / len(base_tag.attrs)

    # weight the scores. text is more important than children, etc.
    print(f"text_score: {text_score}, name_score: {name_score}, children_score: {children_score}, attrs_score: {attrs_score}")
    return (text_score + name_score + children_score + attrs_score) / 4


class DynamicContentDiffer:
    """Class to compare 2 dynamic responses"""
    def __init__(self, base_content):
        self.base_soup = BeautifulSoup(base_content, "html.parser")
        self.base_elements = self.base_soup.find_all()

    def compare_to(self, test_content):
        """
        Compare the base response with the test response using beautiful soup.
        True if the test response is similar to the base response. False otherwise.
        """
        test_soup = BeautifulSoup(test_content, "html.parser")
        test_elements = test_soup.find_all()
        if len(test_elements) == len(self.base_elements):
            for base_tag, test_tag in zip(self.base_elements, test_elements):
                if base_tag == test_tag:
                    ratio = 1
                else:
                    ratio = get_element_ratio(base_tag, test_tag)
                if ratio < MAX_MATCH_RATIO:
                    print(ratio)
                    return False
        else:
            return False
        return True


def generate_matching_regex(string1, string2):
    start = "^"
    end = "$"

    for char1, char2 in zip(string1, string2):
        if char1 != char2:
            start += ".*"
            break

        start += re.escape(char1)

    if start.endswith(".*"):
        for char1, char2 in zip(string1[::-1], string2[::-1]):
            if char1 != char2:
                break

            end = re.escape(char1) + end

    return start + end