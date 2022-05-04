
from whiptail import Whiptail

from components.Game import Game  # pylint: disable=import-error
from components.Player import Player  # pylint: disable=import-error


def getGameMode(whiptail: Whiptail) -> tuple[bool, list[Player], int, bool]:
    # Get hardmode
    hardMode =  not whiptail.yesno(
        'Is this game being played in "hard mode?"',
        default='no'
    )

    # Get number of players
    strNumPlayers, resCode = whiptail.menu(
        "How many players are there (including you)?",
        [
            ["3", "Each player will have 4 cards"],
            ["4", "Each player will have 3 cards"]
        ]
    )
    if resCode == 1 and confirmQuit(whiptail):
        return False, [], 0, False
    numPlayers = int(strNumPlayers)
    numCards = int(12 / numPlayers)

    # Get user's name
    yourName, resCode = whiptail.inputbox("What is your name?", "")
    if resCode == 1 and confirmQuit(whiptail):
        return False, [], 0, False
    players = [Player(yourName, numCards, True)]

    # Get other players
    for i in range(numPlayers - 1):
        name, resCode = whiptail.inputbox(f"What is player {i + 2}'s name?", "")
        if resCode == 1 and confirmQuit(whiptail):
            return False, [], 0, False
        players.append(Player(name, numCards))

    # Get starting player
    strPlayerNumber, resCode = whiptail.menu(
        "Which player will start?",
        [[str(key + 1), player.name] for key, player in enumerate(players)]
    )
    if resCode == 1 and confirmQuit(whiptail):
        return False, [], 0, False
    numStarter = int(strPlayerNumber) - 1

    # Return Success, player list, starting player, hardMode
    return True, players, numStarter, hardMode

def confirmQuit(whiptail: Whiptail) -> bool:
    return not whiptail.yesno(
        "Are you sure you want to quit?",
        default="no"
    )

###################
# MAIN LINE LOGIC #
###################
def main() -> None:
    whiptail = Whiptail(title="Baker Street Dozen", width=100)
    proceed, players, numStarter, hardMode = getGameMode(whiptail)
    if not proceed:
        return
    game = Game(players, numStarter, hardMode, whiptail)
    proceed = game.getStartingHand(3 if len(players) == 4 else 4)
    if not proceed:
        return
    while not game.over() and proceed:
        game.showGameState()
        proceed = game.doTurn()


if __name__ == '__main__':
    main()
