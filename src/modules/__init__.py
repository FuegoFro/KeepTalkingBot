import abc
from abc import abstractmethod

from enum import Enum

Type = Enum('Type', [
    'blank',  #
    'clock',  #
    'button',  # TODO clock (FRK and CAR indicators, batteries)
    'complicated_wires',  #
    'maze',  #
    'memory',  #
    'morse_code',  #
    'password',  #
    'simon_says',  #
    'simple_wires',  #
    'symbols',  #
    'whos_on_first',  #
    'wire_sequence',  #
])


class ModuleSolver(object):
    __metaclass__ = abc.ABCMeta

    @abstractmethod
    def get_type(self):
        raise ValueError("Unimplemented abstract method")

    @abstractmethod
    def solve(self, image, offset, sides_info, screenshot_helper):
        raise ValueError("Unimplemented abstract method")


def create_solvers():
    from modules.maze import MazeSolver
    from modules.password import PasswordSolver
    from modules.whos_on_first import WhosOnFirstSolver
    from modules.symbols import SymbolsSolver
    from modules.morse_code import MorseCodeSolver
    from modules.wire_sequence import WireSequenceSolver
    from modules.memory import MemorySolver
    from modules.simple_wires import SimpleWiresSolver
    from modules.simon_says import SimonSaysSolver
    from modules.complicated_wires import ComplicatedWiresSolver
    from modules.button import ButtonSolver

    module_solver_classes = (
        MazeSolver,
        PasswordSolver,
        WhosOnFirstSolver,
        SymbolsSolver,
        MorseCodeSolver,
        WireSequenceSolver,
        MemorySolver,
        SimpleWiresSolver,
        SimonSaysSolver,
        ComplicatedWiresSolver,
        ButtonSolver,
    )

    solvers = {}
    for solver_class in module_solver_classes:
        solver = solver_class()
        module_type = solver.get_type()
        assert module_type not in solvers, "Found multiple solvers for same module type %s" % module_type
        solvers[module_type] = solver
    return solvers
