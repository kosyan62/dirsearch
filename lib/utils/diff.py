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

TEXT_WEIGHT = 2
NAME_WEIGHT = 3
ATTRS_WEIGHT = 1


def get_dict_ratio(base_dict, test_dict):
    """
    Compare 2 dictionaries and return the ratio of similarity.
    """
    if not base_dict and not test_dict:
        return 1
    elif not base_dict or not test_dict:
        return 0
    else:
        score = 0
        all_keys = set(base_dict.keys()).union(set(test_dict.keys()))
        for key in all_keys:
            if key in base_dict.keys() and key in test_dict.keys():
                attr_score = compare_text(base_dict[key], test_dict[key])
                score += attr_score
            else:
                score -= 0.5  # 50% penalty for missing keys
        score = 0 if score < 0 else score / len(base_dict)
        return score


def compare_text(base_text, test_text):
    """
    Compare 2 strings and return the ratio of similarity.
    """
    if not base_text and not test_text:
        return 1
    elif base_text == test_text:
        return 1
    elif not base_text or not test_text:
        return 0
    else:
        return difflib.SequenceMatcher(None, base_text, test_text).quick_ratio()


def get_elements_differ_ratio(base_tag, test_tag):
    """Compare 2 elements and return the ratio of similarity."""
    text_score = compare_text(base_tag.text, test_tag.text)
    name_score = compare_text(base_tag.name, test_tag.name)
    attrs_score = get_dict_ratio(base_tag.attrs, test_tag.attrs)

    # weight the scores. Name is more important than text etc.
    sum_weights = TEXT_WEIGHT + NAME_WEIGHT + ATTRS_WEIGHT
    sum_scores = text_score * TEXT_WEIGHT + name_score * NAME_WEIGHT + attrs_score * ATTRS_WEIGHT
    final_score = sum_scores / sum_weights

    return final_score


def get_pages_differ_ratio(base_tag, test_tag):
    """
    Go through the base response and count all elements diff ratio.
    """
    elements_score = get_elements_differ_ratio(base_tag, test_tag)

    try:
        children_score = 0
        children_len = 0
        for base_child, test_child in zip(base_tag.children, test_tag.children, strict=True):
            children_len += 1
            children_score += compare_text(base_child.name, test_child.name)
        children_score = children_score / children_len
    except ValueError:
        children_score = 0
    except ZeroDivisionError:
        children_score = 1
    final_score = (elements_score + children_score) / 2

    return final_score


class DynamicContentDiffer:
    """Class to compare 2 dynamic responses"""

    def __init__(self, base_content):
        self.base_content = base_content
        self.base_soup = BeautifulSoup(base_content, "html.parser")
        self.base_elements = self.base_soup.find_all()

    def compare_to(self, test_content):
        """
        Compare the base response with the test response using beautiful soup.
        True if the test response is similar to the base response. False otherwise.
        """
        if self.base_content == test_content:  # for static content
            return True
        test_soup = BeautifulSoup(test_content, "html.parser")
        test_elements = test_soup.find_all()
        if not len(test_elements) == len(self.base_elements):
            return False
        for base_tag, test_tag in zip(self.base_elements, test_elements):
            if base_tag != test_tag:
                ratio = get_pages_differ_ratio(base_tag, test_tag)
                if ratio < MAX_MATCH_RATIO:
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
