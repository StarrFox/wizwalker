from typing import Union


class WizWalkerError(Exception):
    """
    Base wizwalker exception, all exceptions raised should inharit from this
    """

    pass


class HookPatternFailed(WizWalkerError):
    """
    Raised when the pattern scan for a hook fails
    """

    def __init__(self):
        super().__init__(
            "A hook search pattern failed. You most likely need to restart the client"
        )


class HookNotActive(WizWalkerError):
    """
    Raised when doing something that requires a hook to be active
    but it is not

    Attributes:
        hook: The hook that is not active
    """

    def __init__(self, hook: str):
        super().__init__(f"{hook} is not active.")
        self.hook = hook


class HookAlreadyActivated(WizWalkerError):
    """
    Raised when trying to activate an active hook

    Attributes:
        hook: The hook that is already active
    """

    def __init__(self, hook: str):
        super().__init__(f"{hook} was already activated.")
        self.hook = hook


class NotEnoughPips(WizWalkerError):
    """
    Raised when trying to use a card that costs more pips then
    are available

    Attributes:
        missing: The amount of missing pips
    """

    def __init__(self, missing: int):
        super().__init__(f"Missing {missing} pips needed.")
        self.missing = missing


class NotEnoughMana(WizWalkerError):
    """
    Raised when trying to use a card that cost more mana than
    is available

    Attributes:
        missing: The amount of missing mana
    """

    def __init__(self, missing: int):
        super().__init__(f"Missing {missing} mana needed.")
        self.missing = missing


class CardNotFound(WizWalkerError):
    """
    Raised when searching for a card brings no results

    Attributes:
        card_name_or_position: The unfound card name or position
    """

    def __init__(self, card_name_or_positon: Union[str, int]):
        super().__init__(
            f"Card with name or position {card_name_or_positon} not found."
        )
        self.card_name_or_positon = card_name_or_positon


class CardAlreadyEnchanted(WizWalkerError):
    """
    Raised when trying to encahnt an already enchanted card
    """

    def __init__(self):
        super().__init__("That card is already enchanted.")


class HotkeyAlreadyRegistered(WizWalkerError):
    def __init__(self, key: str):
        super().__init__(f"{key} already registered")
