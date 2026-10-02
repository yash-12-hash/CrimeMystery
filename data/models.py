from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Suspect:
    id: str
    name: str


@dataclass
class Location:
    id: str
    name: str


@dataclass
class Connection:
    id: str
    from_location_id: str
    to_location_id: str
    travel_time: int


@dataclass
class Crime:
    crime_type: str
    location_id: str
    start_time: str
    end_time: str


@dataclass
class Evidence:
    id: str
    evidence_type: str
    suspect_id: Optional[str]
    location_id: Optional[str]
    time: Optional[str]
    statement: str
    reliability: float = 1.0


@dataclass
class Constraint:
    id: str
    description: str


@dataclass
class Scenario:
    id: str
    crime: Crime
    suspects: List[Suspect] = field(default_factory=list)
    locations: List[Location] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)