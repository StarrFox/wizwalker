from lark import Lark, Transformer

from .script import CombatAction, Command, Loop, MoveSteps, WizWalkerScript


class WizWalkerScriptTransformer(Transformer):
    @staticmethod
    def wizwalker_script(sections):
        loop, battle, *move_steps = sections
        return WizWalkerScript(loop, battle, move_steps)

    @staticmethod
    def loop(loop):
        iterations = None
        commands = []
        for child in loop:
            child = child[0]
            if isinstance(child, int):
                iterations = child

            else:
                commands.append(child)

        return Loop(commands, iterations)

    @staticmethod
    def loop_iterations(iterations):
        return iterations

    @staticmethod
    def loop_command(command):
        return command

    @staticmethod
    def move_command(target):
        return Command("move", target[0])

    @staticmethod
    def stop_command(_):
        return Command("stop", None)

    @staticmethod
    def npc_command(_):
        return Command("npc", None)

    @staticmethod
    def string_with_numbers(data):
        return data[0].value

    @staticmethod
    def number(value):
        return int(value[0].value)

    @staticmethod
    def name(value):
        return value[0].children[0].value

    @staticmethod
    def cardname(value):
        return value[0]

    @staticmethod
    def xy(value):
        x, y = value
        return x, y

    @staticmethod
    def combat_action(value):
        enchant = None
        maybe_enchant = False

        if len(value) > 2:
            enchant = value[2]
            if enchant.data == "maybe_enchant":
                maybe_enchant = True

            enchant = enchant.children[0]

        source, action = value[:2]
        action_type, param = action

        return CombatAction(action_type, param, source, enchant, maybe_enchant)

    @staticmethod
    def combat_target(value):
        return value[0]

    @staticmethod
    def enemy_target(value):
        return "enemy", value[0]

    @staticmethod
    def ally_target(value):
        return "ally", value[0]

    @staticmethod
    def card_target(value):
        return "card", value[0]

    @staticmethod
    def notarget(_):
        return "notarget", None

    @staticmethod
    def target_param(value):
        return value[0]

    @staticmethod
    def battle(value):
        return value

    @staticmethod
    def move_steps(value):
        name = value[0]
        steps = value[1:]
        return MoveSteps(name, steps)


WIZWALKER_SCRIPT_GRAMMER = """
?start: wizwalker_script

wizwalker_script: loop battle move_steps*


loop: "[loop" loop_iterations? "]" loop_command+

loop_iterations: number
loop_command: "do" (move_command | stop_command | npc_command)

move_command: "move" string_with_numbers
stop_command: "stop"
npc_command: "npc"

move_steps: "<move" string_with_numbers ">" xy+


battle: "[battle]" combat_action+

combat_action: cardname "," combat_target ","? (enchant | maybe_enchant)?
combat_target: ally_target | enemy_target | notarget | card_target


cardname: name
enchant: cardname
maybe_enchant: cardname "?"

positional_param: "first" | "second" | "third" | "forth"
target_param: name | number | positional_param


enemy_target: "enemy(" target_param ")"
ally_target: "ally(" (target_param | "self") ")"
card_target: "card(" (name | number) ")"
notarget: "notarget"


name: string
xy: number "," number

number: SIGNED_NUMBER
string: WORD
string_with_numbers: /[\\w\\d]+/


%import common.ESCAPED_STRING
%import common.WORD
%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""

parser = Lark(WIZWALKER_SCRIPT_GRAMMER)


def parse(entry: str):
    parsed = parser.parse(entry)
    transformed = WizWalkerScriptTransformer().transform(parsed)

    return transformed
