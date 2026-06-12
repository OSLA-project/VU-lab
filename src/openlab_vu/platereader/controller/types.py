import enum


class TrayState(enum.StrEnum):
    Unknown = enum.auto()
    Open = enum.auto()
    Closed = enum.auto()
