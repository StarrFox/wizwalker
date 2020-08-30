class WizWalkerError(Exception):
    """
    Base wizwalker exception, all exceptions raised should inharit from this
    """
    pass


class HookNotActive(WizWalkerError):
    def __init__(self, hook):
        super().__init__(f"{hook} is not active.")


class HookAlreadyActivated(WizWalkerError):
    def __init__(self, hook):
        super().__init__(f"{hook} was already activated.")
