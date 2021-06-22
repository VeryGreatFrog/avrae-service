import logging

from .mixins import AutomatibleMixin, DescribableMixin
from .shared import Sourced

log = logging.getLogger(__name__)


class Spell(AutomatibleMixin, DescribableMixin, Sourced):
    entity_type = 'spell'
    type_id = 1118725998

    def __init__(self, name: str, level: int, school: str, casttime: str, range_: str, components: str, duration: str,
                 description: str, homebrew: bool, classes=None, subclasses=None, ritual: bool = False,
                 higherlevels: str = None, concentration: bool = False, image: str = None, **kwargs):
        if classes is None:
            classes = []
        if isinstance(classes, str):
            classes = [cls.strip() for cls in classes.split(',') if cls.strip()]
        if subclasses is None:
            subclasses = []
        if isinstance(subclasses, str):
            subclasses = [cls.strip() for cls in subclasses.split(',') if cls.strip()]

        super().__init__(homebrew=homebrew, **kwargs)

        self.name = name
        self.level = level
        self.school = school
        self.classes = classes
        self.subclasses = subclasses
        self.time = casttime
        self.range = range_
        self.components = components
        self.duration = duration
        self.ritual = ritual
        self.description = description
        self.higherlevels = higherlevels
        self.concentration = concentration
        self.image = image

        if self.concentration and 'Concentration' not in self.duration:
            self.duration = f"Concentration, up to {self.duration}"

    @classmethod
    def from_data(cls, d):  # local JSON
        return cls(
            d['name'], d['level'], d['school'], d['casttime'], d['range'], d['components'], d['duration'],
            d['description'],
            homebrew=False, classes=d['classes'], subclasses=d['subclasses'], ritual=d['ritual'],
            higherlevels=d['higherlevels'], concentration=d['concentration'],
            source=d['source'], entity_id=d['id'], page=d['page'], url=d['url'], is_free=d['isFree']
        ).initialize_automation(d)

    @classmethod
    def from_homebrew(cls, data, source):  # homebrew spells
        data['components'] = parse_homebrew_components(data['components'])
        data["range_"] = data.pop("range")
        return cls(homebrew=True, source=source, **data).initialize_automation(data)

    def get_school(self):
        return {
            "A": "Abjuration",
            "V": "Evocation",
            "E": "Enchantment",
            "I": "Illusion",
            "D": "Divination",
            "N": "Necromancy",
            "T": "Transmutation",
            "C": "Conjuration"
        }.get(self.school, self.school)

    def get_level(self):
        if self.level == 0:
            return "cantrip"
        if self.level == 1:
            return "1st-level"
        if self.level == 2:
            return "2nd-level"
        if self.level == 3:
            return "3rd-level"
        return f"{self.level}th-level"


def parse_homebrew_components(components):
    v = components.get('verbal')
    s = components.get('somatic')
    m = components.get('material')
    if isinstance(m, bool):
        parsedm = "M"
    else:
        parsedm = f"M ({m})"

    comps = []
    if v:
        comps.append("V")
    if s:
        comps.append("S")
    if m:
        comps.append(parsedm)
    return ', '.join(comps)
