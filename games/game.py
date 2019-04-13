import gtbk


class Game:

    def __init__(self, game_name):

        self.game_name = game_name
        self.game = self.get_game()
        self.rounds = self.determine_rounds()
        self.bot_instructions = [[], {'sendmsg': None,
                                      'sendwhisper': None,
                                      'game_instruction': None}]

    def get_game(self, game_name):
        if game_name == 'gtbk':
            return gtbk.gtbk()

    def determine_rounds(self):
        """Determine number of rounds"""

        if self.game.multiple_rounds is False:
            return 0

        elif self.game.multiple_rounds is True:
            return int(self.instructions)

    def check_rounds(self):
        if self.round is False:
            return

        elif self.rounds == 0:
            self.winner()
            self.end()

    def take_chatter_input(self, user, user_input):
        if user not in self.chatter_inputs.keys():
            self.chatter_inputs[user] = user_input

    def winner(self, winning_input=None):
        if winning_input is None:
            pass
        for i in self.chatter_inputs.keys():
            if self.chatter_inputs[i] == winning_input:
                self.award_points(i)

    def award_points(self, user):
        pass

    # instruction functions

    def clear_instructions(self):
        self.bot_instrucions = [[], {'sendmsg': None,
                                     'sendwhisper': None,
                                     'game_instruction': None}]

    def return_instructions(self):
        return self.instructions

    def end(self):
        pass
