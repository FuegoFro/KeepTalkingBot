SYMBOLS = frozenset((
    "tennis",
    "tripod",
    "lambda",
    "zigzag",
    "spaceship",
    "h",
    "backward_c",
    "umlaut",
    "cursive_l",
    "empty_star",
    "inverted_question",
    "copyright",
    "w",
    "zhe",
    "drunk_3",
    "beh",
    "paragraph",
    "soft_sign",
    "smiley",
    "psi",
    "forward_c",
    "slug",
    "filled_star",
    "stitch",
    "ae",
    "eee",
    "omega"
))
SYMBOL_ORDERS = (
    ("tennis", "tripod", "lambda", "zigzag", "spaceship", "h", "backward_c"),
    ("umlaut", "tennis", "backward_c", "cursive_l", "empty_star", "h", "inverted_question"),
    ("copyright", "w", "cursive_l", "zhe", "drunk_3", "lambda", "empty_star"),
    ("beh", "paragraph", "soft_sign", "spaceship", "zhe", "inverted_question", "smiley"),
    ("psi", "smiley", "soft_sign", "forward_c", "paragraph", "slug", "filled_star"),
    ("beh", "umlaut", "stitch", "ae", "psi", "eee", "omega"),
)


def verify_symbol_order():
    for order in SYMBOL_ORDERS:
        assert len(order) == 7
        for symbol in order:
            assert symbol in SYMBOLS
    print "Verified!"


def get_symbol_order(symbols):
    """
    Return array of indices into symbols indicating what order the symbols should be pressed in.
    """
    possible_orders = SYMBOL_ORDERS
    for symbol in symbols:
        possible_orders = filter(lambda order: symbol in order, possible_orders)
    assert len(possible_orders) == 1, "Expected exactly 1 way to solve symbols, found %s" % len(possible_orders)

    press_order = []
    for symbol in possible_orders[0]:
        if symbol in symbols:
            press_order.append(symbols.index(symbol))

    assert len(press_order) == len(set(press_order)), "Found duplicates in press order! Press order=%s" % (press_order,)
    assert len(press_order) == len(symbols),\
        "Expected to press on as many symbols as were passed in. Symbols=%s Press order=%s" % (symbols, press_order)

    return press_order
