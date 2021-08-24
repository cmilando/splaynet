# =============================================================================
# Author: CWM
# Title: Card and Game classes for Innovation
# Notes:
# -
# =============================================================================
import json
import pprint
import flask
from airium import Airium
from app.config import CARD_DATA, CARD_DATA_REVERSE

# /////////////////////////////////////////////////////////////////////////////
class Card():
    """

    """

    def __init__(self, age):
        """
        Card class only has age and options
        :param age: to initialize you just need to know card age
        """

        self.age = age

        # assign the probability of each card
        possible_cards = CARD_DATA[str(age)]
        self.options = {x: 1/len(possible_cards) for x in possible_cards}

    # the str method shows the card age and number of potential options
    def __str__(self):

        return ('Age ' + str(self.age) + '')

    # So that it looks nice in lists
    __repr__ = __str__


# /////////////////////////////////////////////////////////////////////////////
class Innovation():
    """

    """

    def __init__(self, n_players):
        """

        :param n_players:
        """

        # initialize the game state
        self.n_players   = n_players
        self.hand        = {x: [] for x in range(1, n_players + 1)}
        self.score       = {x: [] for x in range(1, n_players + 1)}
        self.board       = {x: [] for x in range(1, n_players + 1)}
        self.achievement = {x: [] for x in range(1, 10)} # 1 to 9
        self.supply      = {x: [] for x in range(1, 11)} # 1 to 10

        # add cards to supply
        # for age 1: 15
        # for age 2-9: 10
        # for age 10: 10
        for _ in range(0, 15):
            self.supply[1].append(Card(1))

        for age in range(2, 9 + 1):
            for _ in range(0, 10):
                self.supply[age].append(Card(age))

        for _ in range(0, 10):
            self.supply[10].append(Card(10))

        # 1 card from supply ages 1 - 9 for the achievements
        for a in self.achievement:
            achievement = self.supply[a].pop(0)      # remove from supply
            self.achievement[a].append(achievement) # add to achievement

    # //////////////////////////////////////////////////////////////////////////
    def reset_probabilities(self, object, card_age):
        """
        Whenever you get more infomration about a card, you need to
        reset probabilities in the places where you removed and added it

        :param object: this is the specific game state being updated
        :param card_age: this is the age of cards in the state being updated
        :return: None
        """
        cards_in_age = [x for x in object if x.age == card_age]
        n_cards_in_age = len(cards_in_age)

        if n_cards_in_age:

            for o in CARD_DATA[str(card_age)]:
                probs_to_merge = []
                for card in cards_in_age:
                    probs_to_merge.append(card.options[o])
                reset_prob = sum(probs_to_merge) / n_cards_in_age
                for card in cards_in_age:
                    card.options[o] = reset_prob

    # //////////////////////////////////////////////////////////////////////////
    def remove_known_card(self, state, known_card):
        """
        Prior to updating probabilities, you need to set the specific
        card option for a known card to 0 if you know its not somewhere
        and then update the rest of the card_specific option probalities

        :param state:
        :param known_card:
        :return:
        """

        x = getattr(self, state)

        for group in x: # could be age or player
            for card in x[group]:
                if known_card in card.options:
                    # get rid of the known card
                    card.options[known_card] = 0.
                    # then reset probabilities to be 0 to 1
                    sum_probs = sum([card.options[key] for key in card.options])
                    for o in card.options:
                        card.options[o] = card.options[o] / sum_probs

    # //////////////////////////////////////////////////////////////////////////
    def peek(self, state, card_age=None, player_num=None):
        """
        Does a nice print out of cards in each pile

        :param state:
        :param card_age:
        :param player_num:
        :return:
        """

        if state in ['supply', 'achievement']:
            origin = getattr(self, state)[card_age]
        else:
            origin = getattr(self, state)[player_num]

        output = []

        for el in origin:
            x = el.options

            x_cleaned = {key: "{0:.4}%".format(round(x[key] * 100, 1))
                         for key in x if x[key] > 0}
            x_REVERSE = {}

            for key in x_cleaned:
                this_val = x_cleaned[key]
                if this_val in x_REVERSE.keys():
                    x_REVERSE[this_val].append(key)
                else:
                    x_REVERSE[this_val] = [key]

            output.append({el: x_REVERSE})

        #return pprint.pformat(output, compact=True)
        return output

    # //////////////////////////////////////////////////////////////////////////
    def dump(self):
        """
        This is how you dump the library to the page to be re-read

        :return: the str of the game state
        """
        output = {}

        output['n_players']   = self.n_players
        output['hand']        = self.hand
        output['score']       = self.score
        output['board']       = self.board
        output['achievement'] = self.achievement
        output['supply']      = self.supply

        return str(flask.json.htmlsafe_dumps(output))

    # //////////////////////////////////////////////////////////////////////////
    def load(self, game_str):
        """

        :param game_str:
        :return:
        """
        game_json = json.loads(game_str)

        self.n_players   = game_json['n_players']
        self.hand        = game_json['hand']
        self.score       = game_json['score']
        self.board       = game_json['board']
        self.achievement = game_json['achievement']
        self.supply      = game_json['supply']

    # //////////////////////////////////////////////////////////////////////////
    def pretty_dump(self):
        """
        use the peek method to pretty dump everything
        each of these needs to be collapse-able

        So pass these to a html element that you build the same way

        Use this for MVP of splaynet output

        :return:
        """

        output = []

        # For each player:
        #     > hand
        #     > score
        for player_num in range(1, self.n_players + 1):
            for state in ['hand', 'score']:
                key = "Player {0} {1}".format(player_num, state)
                value = self.peek(state, player_num=player_num)
                output.append({key: value})

        # For each card age:
        #     > supply
        #     > achievement
        for card_age in range(1, 11):
            key = "Supply Age {0}".format(card_age)
            value = self.peek('supply', card_age=card_age)
            output.append({key: value})

        for card_age in range(1, 10):
            key = "Achievement Age {0}".format(card_age)
            value = self.peek('achievement', card_age=card_age)
            output.append({key: value})

        # now, make it a template string
        # involving the accordions
        a = Airium()
        outer_loop = 1

        with a.div(klass="accordion", id="accordionExample"):
            for game_state in output:

                with a.div(klass="accordion-item"):
                    # header
                    with a.h2(klass="accordion-header", id="heading_{0}".format(outer_loop)):
                        button_kwargs = {
                            "data-bs-toggle": "collapse",
                            "data-bs-target": "#collapse_{0}".format(outer_loop),
                            "aria-expanded": "true",
                            "aria-controls": "collapse_{0}".format(outer_loop)
                        }
                        with a.button(type="button", klass="accordion-button", **button_kwargs):
                            for key in game_state:
                                a(key)
                    # body
                    outer_body_kwargs = {
                        "aria-labelledby":"heading_{0}".format(outer_loop),
                        "data-bs-parent": "#accordionExample"
                    }
                    with a.div(id="collapse_{0}".format(outer_loop), klass="accordion-collapse collapse",
                               **outer_body_kwargs):
                        with a.div(klass="accordion-body"):
                            for key, sub_cards in game_state.items():
                                if sub_cards:
                                    inner_loop = 1
                                    # <div class="accordion" id="subaccordion{{ outer_loop.index}}">
                                    with a.div(klass="accordion", id="subaccordion{0}".format(outer_loop)):
                                        for card in sub_cards:
                                            with a.div(klass="accordion-item"):
                                                # Inner card header
                                                with a.h2(klass="accordion-header", id="heading_{0}_{1}".format(outer_loop, inner_loop)):
                                                    sub_button_kwargs = {
                                                        "data-bs-toggle": "collapse",
                                                        "data-bs-target": "#collapse_{0}_{1}".format(outer_loop, inner_loop),
                                                        "aria-expanded": "true",
                                                        "aria-controls": "collapse_{0}_{1}".format(outer_loop, inner_loop),
                                                    }
                                                    with a.button(type="button", klass="accordion-button", **sub_button_kwargs):
                                                        for card_age, value_dict in card.items():
                                                            a(card_age)

                                                # inner card body
                                                inner_body_kwargs = {
                                                    "aria-labelledby": "heading_{0}_{1}".format(outer_loop, inner_loop),
                                                    "data-bs-parent": "#subaccordion{0}".format(outer_loop)
                                                }
                                                with a.div(id="collapse_{0}_{1}".format(outer_loop, inner_loop),
                                                            klass="accordion-collapse collapse", **inner_body_kwargs):
                                                    with a.div(klass="accordion-body"):
                                                        for card_age, value_dict in card.items():
                                                            for pval, value_list in value_dict.items():
                                                                a("There is a <strong>{0}</strong> chance that this card is:".format(pval))
                                                                with a.ul():
                                                                    for value in value_list:
                                                                        with a.li():
                                                                            a(value)

                                            inner_loop += 1

                    outer_loop += 1

        template_str = str(a)

        return template_str

    # //////////////////////////////////////////////////////////////////////////
    def move_card(self, from_player_num, to_player_num, from_state, to_state,
              card_age = None, card_name = None):
        """

        :param from_player_num:
        :param to_player_num:
        :param from_state:
        :param to_state:
        :param card_age:
        :param card_name:
        :return:
        """
        if not card_age:
            card_age = CARD_DATA_REVERSE[card_name]

        # Set the card origin
        if from_state == 'supply':
            card_origin = getattr(self, from_state)[card_age]
        else:
            card_origin = getattr(self, from_state)[from_player_num]

        # get behavior differs if you only know card age versus card name
        if card_name:

            card_age = CARD_DATA_REVERSE[card_name]

            # The same as for card age, except searching for card_name
            card_prob = 0.
            card_i = 0

            while card_prob == 0.:
                try:
                    if card_name in card_origin[card_i].options:
                        card_prob = card_origin[card_i].options[card_name]
                    card_i += 1
                except:
                    print('from_state = {0}'.format(from_state))
                    print('to_state = {0}'.format(to_state))
                    print('from_player_num = {0}'.format(from_player_num))
                    print('to_player_num = {0}'.format(to_player_num))
                    print('card_age = {0}'.format(card_age))
                    print('card_name = {0}'.format(card_name))
                    print(self.peek(from_state, card_age=card_age, player_num=from_player_num))
                    raise

            # pop from where it is
            if from_state == 'supply': assert card_i == 1
            moved_card = card_origin.pop(card_i - 1)

            # update probabilities on the moved card since you know its name
            for card in moved_card.options:
                if card == card_name:
                    moved_card.options[card] = 1.
                else:
                    moved_card.options[card] = 0.

            # its not anywhere else ...
            self.remove_known_card('hand', card_name)
            self.remove_known_card('score', card_name)
            self.remove_known_card('supply', card_name)
            self.remove_known_card('achievement', card_name)

        # if you don't know card_name, then its only based on age
        else:

            # This is a mechanism to find a card in the origin that matches age
            card_prob = 0.
            card_i = 0
            while card_prob == 0.:
                if card_origin[card_i].age == card_age:
                    card_prob = 1.
                card_i += 1

            # pop the origin card from its location in the stack
            # in hand and score, as position doesn't matter in these
            # make
            if from_state == 'supply': assert card_i == 1
            moved_card = card_origin.pop(card_i - 1)

        # if the card destination is the supply (i.e, a return)
        # you don't reset probabilities because order matters
        # otherwise you are always resetting probs
        if to_state == 'supply':
            card_destination = getattr(self, to_state)[card_age]
            card_destination.append(moved_card)
        else:
            card_destination = getattr(self, to_state)[to_player_num]
            card_destination.append(moved_card)
            self.reset_probabilities(card_destination, card_age)



