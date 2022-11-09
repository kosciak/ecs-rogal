import collections
import functools
import re

from ..data import data_store


"""Stylesheets related stuff.

CSS / Less / Sass inspired cascading stylesheets mechanism.

Features:
 - <Type>#<ID>.<classname>:<pseudo-class> selectors
 - Some basic nesting (like Frame and Label inside Button)
 - Invalid properties are ignored

Pseudo-classes:
 :hover     - mouse hovered
 :active    - mouse pressed
 :focus     - with keyboard focus
 :checked   - toggle button with value > 0
 :disabled

# TODO:
# TODO: Move to rogal.ui ?
Specificty: https://specifishity.com/

Matching selectors against elements in documnent:
https://drafts.csswg.org/selectors/#match-against-element

"""


SEPARATORS = [
    ':',    # Pseudo-class separator
    '.',    # Classname separator
    '#',    # ID separator
            # No separator - base selector
]


SELECTOR_PATTERN = re.compile(
    '^' +
    '(?P<element>[^#.:]+)?' +
    '(?:#(?P<id>[^.:]+))?' +
    '(?:\.(?P<class>[^:]+))?' +
    '(?:\:(?P<pseudo_class>.+))?' +
    '$'
)


class Specificity(collections.namedtuple(
    'Specificity', [
        'ids',
        'classes',
        'elements',
    ])):

    __slots__ = ()

    def __add__(self, other):
        if not other:
            return None
        return Specificity(
            self.ids + other.ids,
            self.classes + other.classes,
            self.elements + other.elements,
        )


class Selector:

    def __init__(self, element_type, id=None, classes=None, pseudo_classes=None):
        self.element = element_type
        self.id = id
        self.classes = set(classes or [])
        self.pseudo_classes = set(pseudo_classes or [])

    @property
    def specificity(self):
        return Specificity(
            0 + bool(self.id),
            bool(self.classes) + bool(self.pseudo_classes),
            0 + bool(self.element),
        )

    def match(self, other):
        if self.element and not self.element == other.element:
            return False
        if self.id and not self.id == other.id:
            return False
        if self.classes and not self.classes.issubset(other.classes):
            return False
        if self.pseudo_classes and not self.pseudo_classes.issubset(other.pseudo_classes):
            return False
        return True

    @staticmethod
    def parse(selector):
        match = SELECTOR_PATTERN.match(selector or '')
        if not match and match.string:
            return
        return Selector(
            match.group('element'),
            id=match.group('id'),
            classes=match.group('class') and match.group('class').split('.'),
            pseudo_classes=match.group('pseudo_class') and match.group('pseudo_class').split(':'),
        )

    def __repr__(self):
        r = []
        if self.element:
            r.append(self.element)
        if self.id:
            r.append(f'#{self.id}')
        if self.classes:
            r.append(f'.{".".join(self.classes)}')
        if self.pseudo_classes:
            r.append(f':{":".join(self.pseudo_classes)}')
        r = ''.join(r)
        return f'<Selector "{r}">'


def parse_selectors(selectors):
    for selector in selectors.split():
        selector = Selector.parse(selector)
        if selector:
            yield selector


@functools.total_ordering
class Rule:

    def __init__(self, style, selectors):
        self.style = style
        self.selectors = list(parse_selectors(selectors))
        self.specificity = self.calc_specificity()

    def calc_specificity(self):
        specificity = Specificity(0, 0, 0)
        for selector in self.selectors:
            specificity += selector.specificity
        return specificity

    def match(self, path):
        rightmost = True
        selectors_gen = reversed(self.selectors)
        selector = next(selectors_gen)
        for element in reversed(path):
            match = selector.match(element)
            if rightmost and not match:
                return False
            if match:
                selector = next(selectors_gen, None)
                if not selector:
                    return True
            rightmost = False
        return False

    def __lt__(self, other):
        return self.specificity < other.specificity

    def __repr__(self):
        return f'<Rule selectors={self.selectors}>'


class StylesheetsManager:

    def __init__(self, ecs=None):
        self._rules = None

    @property
    def rules(self):
        if self._rules is None:
            rules = []
            for selectors, style in data_store.ui_style.data.items():
                for selectors in selectors.split(', '):
                    rules.append(
                        Rule(style, selectors)
                    )
            self._rules = rules
        return self._rules

    def merge_styles(self, source, update):
        """Recursively merge source with update."""
        if not source:
            return update
        if not update:
            return source

        merged = {}
        keys = source.keys() | update.keys()
        for key in keys:
            if key.islower():
                if key in update:
                    merged[key] = update[key]
                else:
                    merged[key] = source[key]
            else:
                merged[key] = self.merge_styles(
                    source.get(key),
                    update.get(key),
                )
        return merged

    def get_matched_rules(self, selectors_path):
        matched_rules = [
            rule for rule in self.rules
            if rule.match(selectors_path)
        ]
        return sorted(matched_rules)

    def get(self, selectors_path):
        style = {}
        matched_rules = self.get_matched_rules(selectors_path)
        # print(selector, matched_rules)
        for rule in matched_rules:
            style = self.merge_styles(style, rule.style)
        return style

