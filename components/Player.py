from bsdtypes.types import Interrogation, Investigation, NumberTracking


class Player():
    def __init__(self, name, isUserPlayer=False):
        self.name = name
        self.hiddenCard = 0
        self.investigations = []
        self.interrogations = []
        self.symbols = {
            "p": {'min': 0, 'max': 3},
            "l": {'min': 0, 'max': 3},
            "f": {'min': 0, 'max': 3},
            "b": {'min': 0, 'max': 3},
            "j": {'min': 0, 'max': 3},
            "n": {'min': 0, 'max': 3},
            "e": {'min': 0, 'max': 3},
            "s": {'min': 0, 'max': 3}
        }
        self.inGame = True
        self.won = False
        self.isUserPlayer = isUserPlayer

    def __repr__(self) -> str:
        return f"Player(name=\"{self.name}\")"

    def getSymbol(self, symbol: str) -> NumberTracking:
        return self.symbols[symbol]

    def setMin(self, symbol: str, val: int) -> None:
        symbolData = self.symbols[symbol]
        oldMin = symbolData['min']
        newMin = max(val, oldMin)
        self.symbols[symbol]['min'] = min(symbolData['max'], newMin)

    def setMax(self, symbol: str, val: int) -> None:
        symbolData = self.symbols[symbol]
        oldMax = symbolData['max']
        newMax = min(val, oldMax)
        self.symbols[symbol]['max'] = max(symbolData['min'], newMax)

    def advanceHiddenCard(self) -> None:
        self.hiddenCard = 0 if self.hiddenCard == 2 else self.hiddenCard + 1

    def symbolSolved(self, symbol: str) -> bool:
        maximum = self.symbols[symbol]['max']
        minimum = self.symbols[symbol]['min']
        return maximum - minimum == 0

    def _getInvestigations(self, symbol: str) -> list[Investigation]:
        return [i for i in self.investigations if i['symbol'] == symbol]

    def _addInvestigation(self, symbol: str, raisedHand: bool):
        existing = [
            i
            for i in self.investigations
            if i['symbol'] == symbol and i['hiddenCard'] == self.hiddenCard
        ]
        if len(existing) == 0:
            self.investigations.append({
                "hiddenCard": self.hiddenCard,
                "symbol": symbol,
                "raisedHand": raisedHand
            })


    def investigate(
        self,
        symbol: str,
        raisedHand: bool,
        hardMode: bool,
        numPlayers: int
    ) -> None:
        self._addInvestigation(symbol, raisedHand)

        if raisedHand:
            self.setMin(symbol, 1)
        else:
            self.setMax(symbol, 0 if not hardMode else 1)

        if hardMode:
            numCards = int(12 / numPlayers)
            # investigations are unique
            investigations = [
                i['raisedHand']
                for i in self._getInvestigations(symbol)
            ]
            numRaised = sum(investigations)
            numInvestigations = len(investigations)

            # Special logic cases
            if numInvestigations > 1 and numRaised == 0:
                # "seen" every card, never raised hands
                self.setMax(symbol, 0)

            if numInvestigations == numCards and numRaised == numInvestigations:
                # "not seen" all cards, never dropped hand
                self.setMin(symbol, 2)



    def _getInterrogations(
        self,
        symbol: str
    ) -> list[Interrogation]:
        return [
            i
            for i in self.interrogations
            if i['symbol'] == symbol
        ]

    def _addInterrogation(self, symbol: str, number: int) -> None:
        existing = [
            i
            for i in self.interrogations
            if i['symbol'] == symbol and i['hiddenCard'] == self.hiddenCard
        ]
        if len(existing) == 0:
            self.interrogations.append({
                "hiddenCard": self.hiddenCard,
                "symbol": symbol,
                "number": number
            })

    def interrogate(
        self,
        symbol: str,
        number: int,
        hardMode: bool
    ) -> None:
        self._addInterrogation(symbol, number)

        self.setMin(symbol, number)
        self.setMax(symbol, number if not hardMode else number + 1)

        # Miscellaneous extra logic for hard mode
        if hardMode:
            interrogations = [
                i['number']
                for i in self._getInterrogations(symbol)
            ]
            deDupedInterrogations = list(set(interrogations))
            allNumsMatch = len(deDupedInterrogations) == len(interrogations)
            if len(interrogations) > 1 and allNumsMatch:
                if number == 0:
                    self.setMax(symbol, 0)
                elif number == 2:
                    self.setMin(symbol, 3)

