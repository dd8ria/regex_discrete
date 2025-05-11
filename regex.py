from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    """base class for finite automaton states"""
    @abstractmethod
    def __init__(self):
        self.next_states = []

    @abstractmethod
    def check_self(self, char):
        """
        check if this state can consume the given character
        """
        pass

    def check_next(self, next_char):
        """
        find the next matching state or reject the string
        """
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    """
    start state (does not consume input)
    """
    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return False


class TerminationState(State):
    """
    end state (accepts end of string)
    """
    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return False


class DotState(State):
    """
    state for '.' wildcard
    """
    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return True


class AsciiState(State):
    """
    state for a specific ASCII character
    """
    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol

    def check_self(self, char):
        return char == self.symbol


class StarState(State):
    """
    state for '*' quantifier (0 or more)
    """
    def __init__(self, base):
        super().__init__()
        self.base = base

    def check_self(self, char):
        return self.base.check_self(char)


class PlusState(State):
    """
    state for '+' quantifier (1 or more)
    """
    def __init__(self, checking_state):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class RegexFSM:
    """
    finite state machine for basic regex matching
    """
    curr_state = StartState()

    def __init__(self, regex_expr):
        prev_state = self.curr_state
        tmp_state = self.curr_state

        for ch in regex_expr:
            new_state = self.__init_next_state(ch, prev_state, tmp_state)
            prev_state.next_states.append(new_state)
            prev_state = new_state
            tmp_state = new_state

        prev_state.next_states.append(TerminationState())
        self.pattern = regex_expr

    def __init_next_state(
        self, next_token, prev_state, tmp_next_state
    ):
        """
        create appropriate state for the given token
        """
        if next_token == ".":
            return DotState()

        if next_token == "*":
            return StarState(tmp_next_state)

        if next_token == "+":
            return PlusState(tmp_next_state)

        if next_token.isascii():
            return AsciiState(next_token)

    def check_string(self, s):
        """
        match the input string against the pattern
        """
        tokens = []
        i = 0
        while i < len(self.pattern):
            ch = self.pattern[i]
            quant = ""
            if i + 1 < len(self.pattern) and self.pattern[i+1] in "*+":
                quant = self.pattern[i+1]
                i += 2
            else:
                i += 1
            tokens.append((ch, quant))

        def match(pattern_ind, str_ind):
            """
            recursive backtracking matcher
            """
            if pattern_ind == len(tokens):
                return str_ind == len(s)

            sym, quant = tokens[pattern_ind]
            def ok(c):
                return sym == "." or c == sym

            if quant == "*":
                if match(pattern_ind+1, str_ind):
                    return True
                indx = str_ind
                while indx < len(s) and ok(s[indx]):
                    indx += 1
                    if match(pattern_ind+1, indx):
                        return True
                return False

            if quant == "+":
                if str_ind >= len(s) or not ok(s[str_ind]):
                    return False
                indx = str_ind + 1
                if match(pattern_ind+1, indx):
                    return True
                while indx < len(s) and ok(s[indx]):
                    indx += 1
                    if match(pattern_ind+1, indx):
                        return True
                return False

            if str_ind < len(s) and ok(s[str_ind]):
                return match(pattern_ind+1, str_ind+1)
            return False

        return match(0, 0)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
    print(regex_compiled.check_string("pupupuuuu"))  # False
