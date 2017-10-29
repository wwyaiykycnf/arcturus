# coding=utf-8
"""classes/functions related to blacklist support"""
import typing


class Blacklist:
    """
    this class is used to check if posts may be downloaded

    a post may be downloaded when it contains none of the blacklisted terms (or groups/combinations of terms on a single
    line of the blacklist).
    """

    def __init__(self, blacklist: typing.List[str]):
        self.blacklist = blacklist
        self.parsed_lines = {}

    def __len__(self):
        return len(self.blacklist)

    def is_blacklisted(self, tags: typing.List[str]) -> bool:
        """
        check an item's attributes and return True or False indicating whether it is allowed based on the blacklist
        :param tags:  the list of all attributes for an item as a list of strings
        :return: True if item is allowed (aka not blacklisted) else False
        """
        tag_set = set(tags)

        for line in self.blacklist:
            blacklist_terms = self.__parse_terms(line)

            all_pos_tags_present = blacklist_terms["pos"] - tag_set == set()
            no_neg_tags_present = blacklist_terms["neg"].intersection(tag_set) == set()

            if all_pos_tags_present and no_neg_tags_present:
                return True  # it was caught by the blacklist.  it is not allowed to be shown

        return False  # nothing in the blacklist prevented it from being shown, so it is allowed

    def __parse_terms(self, blacklist_line: str) -> {"pos": set(), "meta": set(), "neg": set()}:
        """
        converts one line of the blacklist into a dict containing the terms and their types

        a blacklist line may consist of several "types" of terms, which all have slightly different handling:
        - "meta" terms have the ':' character in them and are mostly unsupported at this time (treated as pos terms)
        - "neg" (negative) terms start with the '-' character.  if the term *IS NOT* in the post, the post is not shown
        - "orr" (OR) terms start with the '~' character.  if *ANY* of these terms are in the post, it is not shown
        - "pos" terms don't meet any of the above criteria. if *ALL* of these terms are in the post, it is not shown

        :param blacklist_line: line from blacklist file
        :return: dictionary containing lists for each of the 4 types above
        """

        if blacklist_line not in self.parsed_lines:

            parsed = {"pos": set(), "meta": set(), "neg": set()}

            for term in blacklist_line.split(' '):
                if ':' in term:
                    parsed["meta"].add(term)  # TODO: meta terms are not supported now ("meta" field is never checked)
                    parsed["pos"].add(term)
                elif term.startswith('-'):
                    parsed["neg"].add(term[1:])
                else:
                    parsed["pos"].add(term)\

            self.parsed_lines[blacklist_line] = parsed

        return self.parsed_lines[blacklist_line]
