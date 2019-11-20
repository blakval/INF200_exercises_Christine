# -*- coding: utf-8 -*-
import random

__author__ = 'Christine Brinchmann', 'Marie Kolvik Valøy'
__email__ = 'christibr@nmbu.no', 'mvaloy@nmbu.no'


class Board:
    """
    Creates a board for the snakes and ladders game. The standard board
    consists of default ladders and snakes as well as a default goal. The
    standard board is created by default.
    """

    def __init__(self,
                 ladders=((1, 40), (8, 10), (36, 52), (43, 62), (49, 79),
                          (65, 82), (68, 85)),
                 chutes=((24, 5), (33, 3), (42, 30), (56, 37), (64, 27),
                         (74, 12), (87, 70)),
                 goal=90):
        self.ladders = ladders
        self.chutes = chutes
        self.goal = goal

    def goal_reached(self, position):
        """ Return True if the goal is reached, and False otherwise. """
        if self.goal <= position:
            return True
        else:
            return False

    def position_adjustment(self, position):
        """

        Parameters
        ----------
        position:
            the position of the player

        Returns
        -------
        0:
            if the players position is not at the start of a snake or ladder
        num_step:
            if the players position is at the start of a snake or ladder, the
            number of position the player must move forward or backward due to
            a ladder or a snake is returned

        """
        for inner_tuple1, inner_tuple2 in zip(self.ladders, self.chutes):
            if position == inner_tuple1[0]:
                return inner_tuple1[1] - inner_tuple1[0]
            elif position == inner_tuple2[0]:
                return inner_tuple2[1] - inner_tuple2[0]
        return 0


class Player:
    """
    Creates a player with a specified board (the standard board is default),
    and keeps track of the players position.
    """
    def __init__(self, board=Board()):
        self.board = board
        self.position = 0

    def move(self):
        """
        Moves the player by implementing a dice cast. If the players position,
        after the dice cast, is at the start of a ladder or a snake, the
        players position is updated accordingly.
        """
        throw = random.randint(1, 6)
        self.position += throw
        self.position += self.board.position_adjustment(self.position)


class ResilientPlayer(Player):
    """
    Subclass of Player, takes extra steps for the next move, but only after
    the player has gone down a snake.
    """
    def __init__(self, board=Board(), extra_steps=1):
        super().__init__(board)
        self.extra_steps = extra_steps
        self.extra_move_flag = False

    def move(self):
        """
        If the player is at the bottom of a snake, it takes a given
        number of extra steps in the next move.
        """
        throw = random.randint(1, 6)
        if self.extra_move_flag:
            throw += self.extra_steps
            self.extra_move_flag = False

        self.position += throw
        pos_adj = self.board.position_adjustment(self.position)
        if pos_adj < 0:
            self.extra_move_flag = True

        self.position += pos_adj


class LazyPlayer(Player):
    """
    Subclass of Player, takes a given number of steps less for the next move,
    but only after going up a ladder.
    """
    def __init__(self, board=Board(), dropped_steps=1):
        super().__init__(board)
        self.dropped_steps = dropped_steps
        self.dropped_steps_flag = False

    def move(self):
        """
        If the player is at the top of a ladder, it takes a given
        number of steps less. The player will not move if the dropped
        steps are greater than the dice cast.
        """
        throw = random.randint(1, 6)
        if self.dropped_steps_flag:
            if self.dropped_steps > throw:
                throw = 0
            else:
                throw -= self.dropped_steps
            self.dropped_steps_flag = False

        self.position += throw
        pos_adj = self.board.position_adjustment(self.position)
        if pos_adj > 0:
            self.dropped_steps_flag = True

        self.position += pos_adj


class Simulation:
    """
    Implements an entire simulation of the snakes and ladders game.
    Default simulation consists of two standard players with standard
    boards, no seed and randomised order of the players at the start of each
    game.
    """
    default_player = [Player, Player]

    def __init__(self,
                 player_field=None,
                 board=Board(),
                 seed=None,
                 randomize_players=True):
        if not player_field:
            self.player_field = self.default_player
        else:
            self.player_field = player_field

        self.board = board
        random.seed(seed)
        self.randomize_players = randomize_players

        self.results = []
        self.player_field_no_duplicate = list(dict.fromkeys(self.player_field))

    def single_game(self):
        """
        Runs a single game with the players and returns a tuple consisting of
        the number of moves and the type of the winner.
        """
        list_players = []
        for player_class in self.player_field:
            list_players.append(player_class(self.board))

        if self.randomize_players:
            random.shuffle(list_players)

        num_moves = [0]*len(list_players)
        for index, player in enumerate(list_players):
            while player.board.goal_reached(player.position) is False:
                player.move()
                num_moves[index] += 1

        num_moves_winner = min(num_moves)
        winner_index = num_moves.index(num_moves_winner)
        winner = (num_moves_winner, type(list_players[winner_index]).__name__)

        return winner

    def run_simulation(self, num_games):
        """
        Runs a given number of games, stores the result and returns nothing.
        """
        for game in range(num_games):
            self.results.append(self.single_game())

    def get_results(self):
        """
        Returns all results stored by run_simulation() as a list of tuples.
        """
        if not self.results:
            raise RuntimeError('run_simulation() must be called first')
        else:
            return self.results

    def winners_per_type(self):
        """
        Returns a dictionary with the player type and number of wins per type.
        """
        result_dict = {}
        for player in self.player_field:
            result_dict[player.__name__] = 0

        for player in self.player_field_no_duplicate:
            for inner_tuple in self.results:
                if player.__name__ == inner_tuple[1]:
                    result_dict[player.__name__] += 1

        return result_dict

    def durations_per_type(self):
        """
        Returns a dictionary with the player types and lists of game durations
        per type.
        """
        duration_dict = {}
        for player in self.player_field:
            duration_dict[player.__name__] = []

        for player in self.player_field_no_duplicate:
            for inner_tuple in self.results:
                if player.__name__ == inner_tuple[1]:
                    duration_dict[player.__name__].append(inner_tuple[0])

        return duration_dict

    def players_per_type(self):
        """
        Returns a dictionary with the player types and number of participants
        per type.
        """
        players_dict = {}
        for player in self.player_field:
            players_dict[player.__name__] = 0

        for player in self.player_field_no_duplicate:
            for player_original in self.player_field:
                if player == player_original:
                    players_dict[player.__name__] += 1

        return players_dict


if __name__ == '__main__':
    players = [Player, LazyPlayer, LazyPlayer, ResilientPlayer]
    sim = Simulation(players, seed=35)
    sim.run_simulation(13)
    print(sim.winners_per_type())
    print(sim.durations_per_type())
    print(sim.players_per_type())
