import winreg
from os import environ
from pathlib import Path


# if None -> find install
_INSTALL_OVERRIDE = environ.get("WIZWALKER_GAME_DIR")

_DEFAULT_INSTALL_LOCATIONS = frozenset(
    [
        "C:/ProgramData/KingsIsle Entertainment/Wizard101",
        "C:/Program Files (x86)/Steam/steamapps/common/Wizard101",
    ]
)


# (key, sub_key)
_REGISTRY_UNINSTALL_LOCATIONS = frozenset(
    [
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Uninstall\{A9E27FF5-6294-46A8-B8FD-77B1DECA3021}"
        ),
    ]
)


def _valid_checker(func):
    func._is_valid_checker = True
    return func


def _install_method(priority: int = 1):
    def decorator(func):
        func._install_method_priority = priority
        return func

    return decorator


class FileLocationHandler:
    # this probably won't need to be async
    def get_game_install_location(self) -> Path:
        for install_method in self._get_install_methods():
            if install_location := install_method():
                return install_location

        raise FileNotFoundError("Game install not found")

    def _get_install_methods(self) -> list:
        install_methods = []

        for attr_name in dir(self):
            install_method = getattr(self, attr_name)
            method_priority = getattr(install_method, "_install_method_priority", None)

            # it can be 0 i.e bool(0) -> False
            if method_priority is not None:
                install_methods.append((method_priority, install_method))

        sorted_methods = sorted(install_methods, key=lambda e: e[0])

        # return just the methods
        return [element[1] for element in sorted_methods]

    def _confirm_install_valid(self, to_validate: str) -> Path | None:
        to_validate = Path(to_validate).absolute()

        for checker in self._get_valid_checkers():
            if not checker(to_validate):
                return None

        return to_validate

    def _get_valid_checkers(self) -> list:
        valid_checkers = []

        for attr_name in dir(self):
            valid_checker = getattr(self, attr_name)
            if getattr(valid_checker, "_is_valid_checker", None):
                valid_checkers.append(valid_checker)

        return valid_checkers

    @_valid_checker
    def _check_exists(self, game_root: Path) -> bool:
        return game_root.exists()

    @_valid_checker
    def _check_is_dir(self, game_root: Path) -> bool:
        return game_root.is_dir()

    @_valid_checker
    def _check_graphical_client(self, game_root: Path) -> bool:
        graphical_client_path = game_root / "Bin" / "WizardGraphicalClient.exe"
        return graphical_client_path.exists()

    @_valid_checker
    def _check_root_wad(self, game_root: Path) -> bool:
        root_wad_path = game_root / "Data" / "GameData" / "Root.wad"
        return root_wad_path.exists()

    @_install_method(0)
    def _get_install_method_env_override(self) -> str | None:
        if _INSTALL_OVERRIDE is None:
            return None

        return self._confirm_install_valid(_INSTALL_OVERRIDE)

    @_install_method(1)
    def _get_install_method_default_locations(self) -> str | None:
        for default_location in _DEFAULT_INSTALL_LOCATIONS:
            if valid_location := self._confirm_install_valid(default_location):
                return valid_location

    @_install_method(2)
    def _get_install_method_registry(self) -> str | None:
        for key, subkey in _REGISTRY_UNINSTALL_LOCATIONS:
            if registry_location := self._get_install_location_from_registry_keys(key, subkey):
                return self._confirm_install_valid(registry_location)

    @staticmethod
    def _get_install_location_from_registry_keys(key, subkey) -> str | None:
        try:
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS) as key:
                return winreg.QueryValueEx(key, "InstallLocation")[0]
        except OSError:
            return None


# TODO: remove debugging
if __name__ == "__main__":
    import asyncio
    flh = FileLocationHandler()

    async def _test():
        #print(flh._get_install_method_env_override._install_method_priority)
        #print(flh._get_install_method_env_override())
        #print(flh._get_install_methods())

        print(await flh.get_game_install_location())

    asyncio.run(_test())
