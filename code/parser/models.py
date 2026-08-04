from dataclasses import dataclass, field


@dataclass
class Entry:
    text: str
    page: int


@dataclass
class Section:
    nom: str
    page: int
    entries: list[Entry] = field(default_factory=list)

    def add_entry(self, entry: Entry):
        self.entries.append(entry)


@dataclass
class Culture:
    nom: str
    page: int
    sections: list[Section] = field(default_factory=list)

    def add_section(self, section: Section):
        self.sections.append(section)


@dataclass
class Family:
    nom: str
    page: int
    cultures: list[Culture] = field(default_factory=list)

    def add_culture(self, culture: Culture):
        self.cultures.append(culture)

@dataclass
class Document:
    families: list[Family] = field(default_factory=list)

    def add_family(self, family):
        self.families.append(family)

@dataclass
class Chunk:
    id: str
    culture : str
    text: str
    metadata: dict = field(default_factory=dict)