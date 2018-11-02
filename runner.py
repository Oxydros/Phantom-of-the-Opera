from Detective import Detective
from Parsing import Parser, PLAYER_TYPE
from World import World


if __name__ == "__main__":
    print("Launching IA")
    world = World()
    parser = Parser(PLAYER_TYPE.DETECTIVE)
    d = Detective(world)
    while (not world.isGameEnded()):
        #parser get infos
        #ia get instr
        #parser write instr
        pass