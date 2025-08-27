from unitelabs.cdk import sila


class ReadInProgressError(sila.DefinedExecutionError):
    """
    This action can not be performed while a read is in progress.
    """
