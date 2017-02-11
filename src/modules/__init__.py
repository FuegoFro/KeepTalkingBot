import abc
from abc import abstractmethod

from enum import Enum

Type = Enum('Type', [
    'blank',  #
    'clock',  #
    'button',  # TODO FRK and CAR indicators, clock. (batteries)
    'complicated_wires',  # TODO parallel port, (last digit of serial even, batteries)
    'maze',  #
    'memory',  #
    'morse_code',  #
    'password',  #
    'simon_says',  # TODO (serial has vowel)
    'simple_wires',  # TODO (last digit of serial number odd)
    'symbols',  #
    'whos_on_first',  #
    'wire_sequence',  #
])

### Work to do to understand outside:
# Find and understand serial number
#   Last digit of serial is odd
#   Last digit of serial is even
#   Serial number has vowels
# Determine number of batteries
#   More than one battery
#   More than two batteries
# Understand indicator label and light (could just special case the two we care about)
#   Lit indicator with CAR
#   Lit indicator with FRK
# Parallel port



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

    module_solver_classes = (
        MazeSolver,
        PasswordSolver,
        WhosOnFirstSolver,
        SymbolsSolver,
        MorseCodeSolver,
        WireSequenceSolver,
        MemorySolver,
        SimpleWiresSolver,
    )

    solvers = {}
    for solver_class in module_solver_classes:
        solver = solver_class()
        module_type = solver.get_type()
        assert module_type not in solvers, "Found multiple solvers for same module type %s" % module_type
        solvers[module_type] = solver
    return solvers
