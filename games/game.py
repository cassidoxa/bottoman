import importlib

class Game:

    def __init__(self, game_name, instructions):
        
        self.game_name = game_name
        self.game = importlib.import_module(game_name)
        self.instructions = instructions
        self.chatter_inputs = {}
        self.chatter_points = {}

        self.rounds = self.determine_rounds(self.game)

    def determine_rounds(self, game):
        """Determine number of rounds"""

        if self.game.multiple_rounds == False:
            return 0

        elif game.multiple_rounds == True:
            return int(self.instructions)

    def check_rounds(self):
        pass

    def take_chatter_input(self, user, user_input):
        pass

    def determine_winner(self, user_inputs):
        pass

    def return_instructions(self):
        return self.instructions

    def end_game(self)
