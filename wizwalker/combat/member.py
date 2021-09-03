import wizwalker


class CombatMember:
    def __init__(
        self,
        combat_handler: "wizwalker.combat.CombatHandler",
        combatant_control: "wizwalker.memory.DynamicWindow",
    ):
        self.combat_handler = combat_handler

        self._combatant_control = combatant_control

    def get_participant(self):
        """
        Get the underlying participant object
        """
        return self._combatant_control.maybe_combat_participant()

    def get_stats(self):
        """
        Get the underlying game stats object
        """
        part = self.get_participant()
        return part.game_stats()

    def get_health_text_window(self) -> "wizwalker.memory.DynamicWindow":
        """
        Get the health text window
        Useful for targeting
        """
        possible = self._combatant_control.get_windows_with_name("Health")
        if possible:
            return possible[0]

        raise ValueError("Couldn't find health child")

    def get_name_text_window(self) -> "wizwalker.memory.DynamicWindow":
        """
        Get the name text window
        """
        possible = self._combatant_control.get_windows_with_name("Name")
        if possible:
            return possible[0]

        raise ValueError("Couldn't find name child")

    def is_dead(self) -> bool:
        """
        If this member is dead
        """
        part = self.get_participant()
        stats = part.game_stats()
        return stats.current_hitpoints() == 0

    def is_client(self) -> bool:
        """
        If this member is the local client
        """
        owner_id = self.owner_id()
        global_id = self.combat_handler.client.client_object.global_id_full()
        return owner_id == global_id

    def is_player(self) -> bool:
        """
        If this member is a player
        """
        part = self.get_participant()
        return part.is_player()

    def is_monster(self) -> bool:
        """
        If this member is not a player and not a minion
        """
        return not self.is_player() and not self.is_minion()

    def is_minion(self) -> bool:
        """
        If this member is a minion
        """
        part = self.get_participant()
        return part.is_minion()

    def is_boss(self) -> bool:
        """
        If this member is a boss
        """
        part = self.get_participant()
        return part.boss_mob()

    def is_stunned(self) -> bool:
        """
        If this member is stunned
        """
        part = self.get_participant()
        return part.stunned() != 0

    def name(self) -> str:
        """
        Name of this member
        """
        name_window = self.get_name_text_window()
        return name_window.maybe_text()

    # TODO: finish
    # def school_name(self) -> str:
    #     pass

    def owner_id(self) -> int:
        """
        This member's owner id
        """
        part = self.get_participant()
        return part.owner_id_full()

    def template_id(self) -> int:
        """
        This member's template id
        """
        part = self.get_participant()
        return part.template_id_full()

    def normal_pips(self) -> int:
        """
        The number of normal pips this member has
        """
        part = self.get_participant()
        return part.num_pips()

    def power_pips(self) -> int:
        """
        The number of power pips this member has
        """
        part = self.get_participant()
        return part.num_power_pips()

    def shadow_pips(self) -> int:
        """
        The number of shadow pips this member has
        """
        part = self.get_participant()
        return part.num_shadow_pips()

    def health(self) -> int:
        """
        The amount of health this member has
        """
        part = self.get_participant()
        return part.player_health()

    def max_health(self) -> int:
        """
        This member's max health
        """
        stats = self.get_stats()
        return stats.max_hitpoints()

    def mana(self) -> int:
        """
        The amount of mana this member has
        """
        stats = self.get_stats()
        return stats.current_mana()

    def max_mana(self) -> int:
        """
        This member's max mana
        """
        stats = self.get_stats()
        return stats.max_mana()

    def level(self) -> int:
        """
        This member's level
        """
        stats = self.get_stats()
        return stats.reference_level()
