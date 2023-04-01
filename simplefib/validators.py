"""
A helper file with validators and completors
for the prompt_toolkit components used in the CLI.
"""
from typing import List, Callable

from simplefib.db import Database, Subject


def validateFloat(inText: str) -> bool:
    """
    Validates that the input text can be parsed
    as a float.

    :param inText: The text to test against.

    :return: A bool, where true indicates it can be
        parsed, false otherwise
    """
    try:
        x = float(inText)
        return True
    except ValueError:
        return False


def validateInt(inText: str) -> bool:
    """
    Validates that the input text can be parsed
    as an int.

    :param inText: The text to test against.

    :return: A bool, where true indicates it can be
        parsed, false otherwise
    """
    try:
        x = int(inText)
        return True
    except ValueError:
        return False

def getStrListValidator(validInputs : List[str]) -> Callable[[str], bool]:
    """
    Returns a validator that checks if the given
    input is in the list of valid inputs.

    :param validInputs: The list of valid inputs.

    :return: A bool, where true indicates it is in the
        list, false otherwise
    """
    returnLambda: Callable[[str], bool] = lambda inText: inText in set(validInputs)

    return returnLambda

def getSubjectNames(db: Database) -> List[str]:
    """
    Returns a list of subject names from the database.
    Mainly a helper function for other functions
    that need subject names.

    :param db: The database to get the subject names from.
    :return: A list of subject names.
    """
    subjNames: List[str] = []
    for record in db.recordDict.values():
        if type(record) != Subject:
            continue
        subjNames.append(record.name)

    return subjNames


def getSubjectNameValidator(db: Database) -> Callable[[str], bool]:
    """
    Returns a name validator that checks if the given
    subject name is in the database.

    :param inText: The text to test against.

    :return: A bool, where true indicates it can be
        parsed, false otherwise
    """
    subjNames: List[str] = getSubjectNames(db)

    return getStrListValidator(subjNames)
