"""
Handles logic for doing forward
predictions of topic time-to-study.
"""
from typing import Dict, Tuple, List
from datetime import datetime, timedelta, timezone

from simplefib.db import Database, Topic, Subject
from simplefib.fib import fibNumbers
from simplefib.uid import UID


class Predictor:
    """
    This class takes in a dataset
    as input, and internally
    computes the topic time-to-study
    for each topic in the dataset.

    :param dataset: The dataset to
        use for computing the
        topic time-to-study.
    """

    def __init__(self, dBase: Database) -> None:
        self.dBase: Database = dBase

        # This lookup contains a lookup from Task UID
        # to predicted date to study.
        self.timeLookup: Dict[UID, datetime] = {}

    def predict(self) -> Dict[UID, datetime]:
        """
        Computes predicted study dates for all topics,
        and returns.

        :return: Returns a mapping from topic UID : predicted
            datetime.
        """
        # First, pull out the names of all subjects, alongisde
        # their weights and biases
        subjectWAndTup: Dict[UID, Tuple[float, int]] = {}
        for subject in self.dBase.recordDict.values():
            if isinstance(subject, Subject):
                subjectWAndTup[subject.uid] = (subject.weight, subject.bias)

        # Now, iterate over database, and compute predicted date of study for
        # all topics
        resultDict: Dict[UID, datetime] = {}
        for item in self.dBase.recordDict.values():
            if type(item) == Topic:
                rawFibPred: int = fibNumbers.getNthFibNumber(item.fibNumber)
                subjectWeight: float = subjectWAndTup[item.subjectUID][0]
                subjectBias: int = subjectWAndTup[item.subjectUID][1]

                actualPred: int = round(rawFibPred * subjectWeight + subjectBias)
                resultDict[item.uid] = datetime.now(tz=timezone.utc) + timedelta(
                    days=actualPred
                )
        
        self.timeLookup = resultDict

        return resultDict
