from tabulate import tabulate
from whiptail import Whiptail

from bsdtypes.types import SymbolTracking
from components.Player import Player
from components.Suspect import Suspect


class Game():
    def __init__(self, players: list[Player], startingPlayer: int, hardMode: bool, whiptail: Whiptail):
        self.suspects = [
            Suspect('Sebastian Moran', ['s', 'f']),
            Suspect('Irene Adler', ['s', 'l', 'n']),
            Suspect('Inspector Lestrade', ['b', 'e', 'j']),
            Suspect('Inspector Gregson', ['b', 'f', 'j']),
            Suspect('Inspector Baynes', ['b', 'l']),
            Suspect('Inspector Bradstreet', ['b', 'f']),
            Suspect('Inspector Hopkins', ['b', 'p', 'e']),
            Suspect('Sherlock Holmes', ['p', 'l', 'f']),
            Suspect('John Watson', ['p', 'e', 'f']),
            Suspect('Mycroft Holmes', ['p', 'l', 'j']),
            Suspect('Mrs. Hudson', ['p', 'n']),
            Suspect('Mary Morstan', ['j', 'n']),
            Suspect('James Moriarty', ['s', 'l'])
        ]

        self.symbols = {
            "p": {"totalInGame": 5, "name": "Pipe"},
            "l": {"totalInGame": 5, "name": "Lightbulb"},
            "f": {"totalInGame": 5, "name": "Fist"},
            "b": {"totalInGame": 5, "name": "Badge"},
            "j": {"totalInGame": 4, "name": "Journal"},
            "n": {"totalInGame": 3, "name": "Necklace"},
            "e": {"totalInGame": 3, "name": "Eye"},
            "s": {"totalInGame": 3, "name": "Skull"}
        }

        self.players = players
        self.currPlayerIndex = startingPlayer

        self.hardMode = hardMode

        self.whiptail = whiptail

    def showGameState(self) -> None:
        gameStateString = self.getGameStateString()
        suspectString = self.getSuspectString()
        self.whiptail.msgbox(gameStateString + "\n\n\n" + suspectString)

    def getSuspectString(self) -> str:
        murderer = self.calculateMurderer()
        headers = ["Suspect"]
        symbolHeaders = [item['name'][:5] for item in self.symbols.values()]
        headers.extend(symbolHeaders)
        tableData = []
        for suspect in self.suspects:
            if suspect.cleared(murderer):
                suspectMark = "\u2717" # Ballot X
            else:
                suspectMark = "\u2753" # Question Mark
            row = [f"{suspectMark} {suspect.name}"]
            for symbol in self.symbols:
                conclusive = suspect.isConclusive(symbol, murderer)
                matchingEvidence = suspect.matchingEvidence(symbol, murderer)
                if not conclusive:
                    symbolString = "\u2753" # Question Mark
                elif matchingEvidence:
                    symbolString = "\u2705" # Check
                else:
                    symbolString = "\u2717" # Ballot X
                row.append(symbolString)
            tableData.append(row)

        return tabulate(tableData, headers=headers)

    def getGameStateString(self) -> str:
        headers = ["Investigator"]
        symbolHeaders = [item['name'][:5] for item in self.symbols.values()]
        headers.extend(symbolHeaders)
        tableData = []
        for player in self.players:
            line = []
            line.append(player.name)
            for symbol in self.symbols:
                minimumSymbols = player.getSymbol(symbol)['min']
                maximumSymbols = player.getSymbol(symbol)['max']
                if minimumSymbols == maximumSymbols:
                    line.append(f"{minimumSymbols}")
                else:
                    line.append(f"{minimumSymbols} - {maximumSymbols}")
            tableData.append(line)
        tableData.append(["-----"] * 9)
        line = ['Murderer']
        murderer = self.calculateMurderer()
        for symbol, symbolData in murderer.items():
            murdererMin = symbolData['min']
            murdererMax = symbolData['max']
            if murdererMin == murdererMax:
                line.append(f"{murdererMin} \u2705")
            else:
                line.append(f"{murdererMin} - {murdererMax}")
        tableData.append(line)
        return tabulate(tableData, headers=headers)


    def calculateMurderer(self) -> SymbolTracking:
        murderer = {}
        for symbol, symbolData in self.symbols.items():
            total = symbolData['totalInGame']
            minInPlayersHands = self.calculateMinFound(symbol)
            maxInPlayersHands = self.calculateMaxFound(symbol)
            murdererMin = total - maxInPlayersHands
            murdererMax = total - minInPlayersHands
            murdererMin = max(0, murdererMin)
            murdererMax = min(1, murdererMax)
            murderer[symbol] = {"max": murdererMax, "min": murdererMin}
        return murderer

    def calculateMinFound(self, symbol: str) -> int:
        return sum([
            player.getSymbol(symbol)['min']
            for player in self.players
        ])

    def calculateMaxFound(self, symbol: str) -> int:
        return sum([
            player.getSymbol(symbol)['max']
            for player in self.players
        ])

    def getStartingHand(self, targetNumber: int) -> bool:
        selected = []
        while len(selected) != targetNumber:
            selected, resCode = self.whiptail.checklist(
                f"Who is in your starting hand (Select {targetNumber})?",
                [
                    [str(key + 1), suspect.name, "0"]
                    for key, suspect in enumerate(self.suspects)
                ]
            )
            if resCode == 1 and self.confirmQuit():
                return False
        for key in [int(key) - 1 for key in selected]:
            self.suspects[key].inHand = True

        symbolsInHand = [
            symbol
            for suspect in self.suspects
            if suspect.inHand
            for symbol in suspect.symbols
        ]
        for symbol, symbolData in self.symbols.items():
            gameTotal = symbolData['totalInGame']
            userHas = len([x for x in symbolsInHand if x == symbol])
            for player in self.players:
                if player.isUserPlayer:
                    # First player, i.e. the user
                    player.setMin(symbol, userHas)
                    player.setMax(symbol, userHas)
                else:
                    newMaxToBeFound = gameTotal - self.calculateMinFound(symbol)
                    player.setMax(symbol, newMaxToBeFound)
        return True

    def doTurn(self) -> bool:
        showOptions = True
        while showOptions:
            choice, resCode = self.whiptail.menu(
                f"What is {self.getCurrentPlayer().name} doing?",
                [
                    ["Game State", "View the current game state"],
                    ["Investigate", "Ask the table for a symbol"],
                    ["Interrogate", "Ask an individual about a symbol"]
                ]
            )
            if resCode == 1 and self.confirmQuit():
                return False

            showOptions = False
            if choice == 'Investigate':
                actionSuccessful = self.investigate()
                if actionSuccessful:
                    self.calculatePlayerhands()
                    self.advancePlayer()
            elif choice == 'Interrogate':
                actionSuccessful = self.interrogate()
                if actionSuccessful:
                    self.calculatePlayerhands()
                    self.advancePlayer()
            elif choice == 'Game State':
                self.showGameState()
                showOptions = True

        return True

    def calculatePlayerhands(self) -> None:
        for symbol, symbolData in self.symbols.items():
            minLocated = self.calculateMinFound(symbol)
            maxLocated = self.calculateMaxFound(symbol)
            maxOutstanding = symbolData['totalInGame'] - minLocated
            minOutstanding = symbolData['totalInGame'] - maxLocated
            for player in self.getNonUserPlayers():
                player.setMax(symbol, maxOutstanding)
                if minOutstanding == 1:
                    player.setMin(symbol, player.getSymbol(symbol)['max'])

    def confirmQuit(self) -> bool:
        return not self.whiptail.yesno(
            "Are you sure you want to quit?",
            default="no"
        )

    def advancePlayer(self) -> None:
        lastPlayer = self.currPlayerIndex == len(self.players) - 1
        self.currPlayerIndex = 0 if lastPlayer else self.currPlayerIndex + 1
        self.getCurrentPlayer().advanceHiddenCard()

    def getCurrentPlayer(self) -> Player:
        return self.players[self.currPlayerIndex]

    def getNonCurrentPlayers(self) -> list[Player]:
        return [
            player
            for index, player in enumerate(self.players)
            if index != self.currPlayerIndex
        ]

    def getUserPlayer(self) -> Player:
        return self.players[0]

    def getNonUserPlayers(self) -> list[Player]:
        return [player for player in self.players if not player.isUserPlayer]

    def getAnsweringPlayers(self) -> list[Player]:
        return [
            player
            for player in self.getNonCurrentPlayers()
            if not player.isUserPlayer
        ]

    def over(self) -> bool:
        someoneWon = len([
            player
            for player in self.players
            if player.won
        ]) > 0
        onlyOneLeft = len([
            player
            for player in self.players
            if player.inGame
        ]) == 1
        return someoneWon or onlyOneLeft

    def investigate(self) -> bool:
        answeringResCode = 1
        answeringPlayers = self.getAnsweringPlayers()
        while answeringResCode != 0:
            symbol, symbolRescode = self.symbolMenu(
                f"What is {self.getCurrentPlayer().name} asking about?"
            )
            if symbolRescode == 1:
                # Return to turn menu
                return False

            answeringKeys, answeringResCode = self.whiptail.checklist(
                "Who raised their hands?",
                [
                    [
                        str(key + 1),
                        player.name,
                        "0" if player.getSymbol(symbol)['min'] == 0 else "1"
                    ]
                    for key, player in enumerate(answeringPlayers)
                ]
            )
            if answeringResCode == 0:
                answeringKeys = [int(key) - 1 for key in answeringKeys]
                for key, player in enumerate(answeringPlayers):
                    raisedHand = key in answeringKeys
                    player.investigate(
                        symbol,
                        raisedHand,
                        self.hardMode
                    )
        return True

    def symbolMenu(self, message: str) -> tuple[str, int]:
        return self.whiptail.menu(
            message,
            [[key, val['name']] for key, val in self.symbols.items()]
        )

    def interrogate(self) -> bool:
        nonCurrentPlayers = self.getNonCurrentPlayers()
        playerQuestionSuccess = False
        symbolQuestionSuccess = False
        numberQuestionSuccess = False
        finished = False
        while not finished:
            if not playerQuestionSuccess:
                key, resCode = self.whiptail.menu(
                    f"Who is {self.getCurrentPlayer().name} interrogating?",
                    [
                        [str(key + 1), player.name]
                        for key, player in enumerate(nonCurrentPlayers)
                    ]
                )
                playerQuestionSuccess = resCode == 0
                if not playerQuestionSuccess:
                    # Return to turn menu
                    return False

            if not symbolQuestionSuccess and playerQuestionSuccess:
                interrogatee = nonCurrentPlayers[int(key) - 1]
                if interrogatee.isUserPlayer:
                    return True
                symbol, resCode = self.symbolMenu("What are they asking about?")
                symbolQuestionSuccess = resCode == 0
                # Possibly return to interrogatee question
                playerQuestionSuccess = symbolQuestionSuccess

            if not numberQuestionSuccess and symbolQuestionSuccess:
                symbolData = interrogatee.getSymbol(symbol)
                strNumber, resCode = self.whiptail.menu(
                    f"How many did {interrogatee.name} say they have? ",
                    [str(x) for x in range(symbolData['min'], symbolData['max'] + 1)]
                )
                numberQuestionSuccess = resCode == 0
                # Possibly return to symbol question
                symbolQuestionSuccess = numberQuestionSuccess
                # Are we completely finished?
                finished = numberQuestionSuccess

            if finished:
                number = int(strNumber)
                interrogatee.interrogate(symbol, number, self.hardMode)
                return True
