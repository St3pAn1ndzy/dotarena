from enum import StrEnum


class BattleStatus(StrEnum):
    pending = "pending"
    active = "active"
    finished = "finished"
    cancelled = "cancelled"
