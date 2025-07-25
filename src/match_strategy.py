from abc import ABC, abstractmethod


class MatchStrategy(ABC):
    @abstractmethod
    def matches(self, text: str) -> bool:
        pass


class RegexMatch(MatchStrategy):
    def __init__(self, pattern: str):
        import re
        self.pattern = pattern
        self.regex = re.compile(pattern)

    def matches(self, text: str) -> bool:
        return bool(self.regex.fullmatch(text.strip()))
