from typing import TypedDict


class NumberTracking(TypedDict):
    max: int
    min: int

class SymbolTracking(TypedDict):
    p: NumberTracking
    l: NumberTracking
    f: NumberTracking
    b: NumberTracking
    j: NumberTracking
    n: NumberTracking
    e: NumberTracking
    s: NumberTracking

class Investigation(TypedDict):
    hiddenCard: int
    symbol: str
    raisedHand: bool

class Interrogation(TypedDict):
    hiddenCard: int
    symbol: str
    number: int
