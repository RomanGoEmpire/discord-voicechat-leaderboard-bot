from discord import Colour, Permissions


class Role:
    def __init__(self, name: str, hours: int, color: str, permissions: Permissions):
        self.name = name
        self.hours = hours
        self.colour = self._verify_color(color)
        self.permissions = permissions

    @staticmethod
    def _verify_color(color: str) -> Colour:
        try:
            return Colour.from_str(color)
        except ValueError:
            raise ValueError(f"Invalid color: {color}")

    def __str__(self) -> str:
        return f"{self.name} - {self.hours} hours"

    def __repr__(self) -> str:
        return str(self)
