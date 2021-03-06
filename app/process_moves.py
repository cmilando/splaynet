from app.class_board_v2 import Innovation

def process_moves(form, move_queue, n_players):

    # initialize
    game = Innovation(n_players=n_players)

    # draw my first cards
    game.move_card(from_player_num=1, to_player_num=1, from_state='supply',
                   to_state='hand', card_name=form['card_1'])

    game.move_card(from_player_num=1, to_player_num=1, from_state='supply',
                   to_state='hand', card_name=form['card_2'])

    # draw everyone else's first cards
    for p in range(2, n_players + 1):
        game.move_card(from_player_num=p, to_player_num=p, from_state='supply',
                       to_state='hand', card_age=1)

        game.move_card(from_player_num=p, to_player_num=p, from_state='supply',
                       to_state='hand', card_age=1)

    # then process move_queue
    print("{0} moves to process".format(len(move_queue)))

    # pre print all of them
    i = 1
    for move in move_queue:

        print("Move {0}: {1}".format(i, move['move_string']))
        i = i + 1

    for move in move_queue:

        print(move['move_string'])

        game.move_card(from_player_num=move['from_player_num'],
                       to_player_num=move['to_player_num'],
                       from_state=move['from_state'],
                       to_state=move['to_state'],
                       card_age=move['card_age'],
                       card_name=move['card_name'])

        # debug
        # game.peek("hand", player_num=2, pretty_print=True)

    # return
    return game.pretty_dump()

