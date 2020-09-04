class WizWalkerError(Exception):
    """
    Base wizwalker exception, all exceptions raised should inharit from this
    """

    pass


class HookNotActive(WizWalkerError):
    def __init__(self, hook):
        super().__init__(f"{hook} is not active.")
        self.hook = hook


class HookAlreadyActivated(WizWalkerError):
    def __init__(self, hook):
        super().__init__(f"{hook} was already activated.")
        self.hook = hook


class NotEnoughPips(WizWalkerError):
    def __init__(self, missing):
        super().__init__(f"Missing {missing} pips needed.")
        self.missing = missing


class NotEnoughMana(WizWalkerError):
    def __init__(self, missing):
        super().__init__(f"Missing {missing} mana needed.")
        self.missing = missing


class CardNotFound(WizWalkerError):
    def __init__(self, card_name_or_positoon):
        super().__init__(
            f"Card with name or position {card_name_or_positoon} not found."
        )
        self.card_name_or_positoon = card_name_or_positoon


class CardAlreadyEnchanted(WizWalkerError):
    def __init__(self):
        super().__init__("That card is already enchanted.")
