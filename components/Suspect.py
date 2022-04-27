from bsdtypes.types import SymbolTracking


class Suspect():
    def __init__(self, name, symbols):
        self.name = name
        self.symbols = symbols
        self.inHand = False
        self.guessed = False

    def setInHand(self) -> None:
        self.inHand = not self.inHand

    def cleared(self, murderer: SymbolTracking) -> bool:
        return self.inHand or self.guessed or any([
            self.isConclusive(symbol, murderer)
            and not self.matchingEvidence(symbol, murderer)
            for symbol
            in murderer
        ])

    def isConclusive(self, symbol: str, murderer: SymbolTracking) -> bool:
        return murderer[symbol]['min'] == murderer[symbol]['max']

    def matchingEvidence(
        self,
        symbol: str,
        murderer: SymbolTracking
    ) -> bool:
        if murderer[symbol]['max'] == 0:
            # The murderer doesn't have the symbol
            return symbol not in self.symbols
        elif murderer[symbol]['min'] == 1:
            # The murderer has the symbol
            return symbol in self.symbols

        # Inconclusive
        return False
