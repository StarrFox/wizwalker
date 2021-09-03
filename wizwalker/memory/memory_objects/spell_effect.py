from wizwalker.memory.memory_object import DynamicMemoryObject, PropertyClass
from .enums import SpellEffects, EffectTarget


class SpellEffect(PropertyClass):
    def read_base_address(self) -> int:
        raise NotImplementedError()

    def effect_type(self) -> SpellEffects:
        return self.read_enum(72, SpellEffects)

    def write_effect_type(self, effect_type: SpellEffects):
        self.write_enum(72, effect_type)

    def effect_param(self) -> int:
        return self.read_value_from_offset(76, "int")

    def write_effect_param(self, effect_param: int):
        self.write_value_to_offset(76, effect_param, "int")

    def string_damage_type(self) -> str:
        return self.read_string_from_offset(88)

    def write_string_damage_type(self, string_damage_type: str):
        self.write_string_to_offset(88, string_damage_type)

    def damage_type(self) -> int:
        return self.read_value_from_offset(80, "unsigned int")

    def write_damage_type(self, damage_type: int):
        self.write_value_to_offset(80, damage_type, "unsigned int")

    def pip_num(self) -> int:
        return self.read_value_from_offset(128, "int")

    def write_pip_num(self, pip_num: int):
        self.write_value_to_offset(128, pip_num, "int")

    def act_num(self) -> int:
        return self.read_value_from_offset(132, "int")

    def write_act_num(self, act_num: int):
        self.write_value_to_offset(132, act_num, "int")

    def effect_target(self) -> EffectTarget:
        return self.read_enum(140, EffectTarget)

    def write_effect_target(self, effect_target: EffectTarget):
        self.write_enum(140, effect_target)

    def num_rounds(self) -> int:
        return self.read_value_from_offset(144, "int")

    def write_num_rounds(self, num_rounds: int):
        self.write_value_to_offset(144, num_rounds, "int")

    def param_per_round(self) -> int:
        return self.read_value_from_offset(148, "int")

    def write_param_per_round(self, param_per_round: int):
        self.write_value_to_offset(148, param_per_round, "int")

    def heal_modifier(self) -> float:
        return self.read_value_from_offset(152, "float")

    def write_heal_modifier(self, heal_modifier: float):
        self.write_value_to_offset(152, heal_modifier, "float")

    def spell_template_id(self) -> int:
        return self.read_value_from_offset(120, "unsigned int")

    def write_spell_template_id(self, spell_template_id: int):
        self.write_value_to_offset(120, spell_template_id, "unsigned int")

    def enchantment_spell_template_id(self) -> int:
        return self.read_value_from_offset(124, "unsigned int")

    def write_enchantment_spell_template_id(
        self, enchantment_spell_template_id: int
    ):
        self.write_value_to_offset(
            124, enchantment_spell_template_id, "unsigned int"
        )

    def act(self) -> bool:
        return self.read_value_from_offset(136, "bool")

    def write_act(self, act: bool):
        self.write_value_to_offset(136, act, "bool")

    def cloaked(self) -> bool:
        return self.read_value_from_offset(157, "bool")

    def write_cloaked(self, cloaked: bool):
        self.write_value_to_offset(157, cloaked, "bool")

    def armor_piercing_param(self) -> int:
        return self.read_value_from_offset(160, "int")

    def write_armor_piercing_param(self, armor_piercing_param: int):
        self.write_value_to_offset(160, armor_piercing_param, "int")

    def chance_per_target(self) -> int:
        return self.read_value_from_offset(164, "int")

    def write_chance_per_target(self, chance_per_target: int):
        self.write_value_to_offset(164, chance_per_target, "int")

    def protected(self) -> bool:
        return self.read_value_from_offset(168, "bool")

    def write_protected(self, protected: bool):
        self.write_value_to_offset(168, protected, "bool")

    def converted(self) -> bool:
        return self.read_value_from_offset(169, "bool")

    def write_converted(self, converted: bool):
        self.write_value_to_offset(169, converted, "bool")

    def rank(self) -> int:
        return self.read_value_from_offset(208, "int")

    def write_rank(self, rank: int):
        self.write_value_to_offset(208, rank, "int")

    def maybe_effect_list(
        self, *, check_type: bool = False
    ) -> list["DynamicSpellEffect"]:
        if check_type:
            type_name = self.maybe_read_type_name()
            if type_name not in ("RandomSpellEffect", "RandomPerTargetSpellEffect"):
                raise ValueError(
                    f"This object is a {type_name} not a RandomSpellEffect/RandomPerTargetSpellEffect."
                )

        effects = []

        for addr in self.read_shared_linked_list(224):
            effects.append(DynamicSpellEffect(self.hook_handler, addr))

        return effects


class DynamicSpellEffect(DynamicMemoryObject, SpellEffect):
    pass
