class Player:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
    def reply(self):
        player_line = input("Your line: ")
        return player_line