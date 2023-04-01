"""
Contains all logic related to database
record types, and the database itself.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from datetime import timezone
from typing import List, Dict, TypeVar, Callable, Type, Optional
import json

from simplefib.uid import UID


class Record(ABC):
    """
    An abstract base class for all database records.
    Creates a single interface for all record
    types.

    :param uid: The UID of this Record Type.
    """

    def __init__(self, uid: UID) -> None:
        self.uid: UID = uid

    @abstractmethod
    def toJSON(self) -> dict:
        """
        All record types need to support
        conversions to dictionary, which
        itself should be JSON serializable.

        Aside from encoding(done here),
        decoding needs to also be implemented
        on each sub-type.

        :return: A JSON dict where all the types
            in it are serializable by Python's
            native JSON module
        """
        pass

    @staticmethod
    @abstractmethod
    def fromJSON(dictIn: dict) -> "Record":
        """
        For each record type, we need to implement
        a static method that can convert a JSON
        dict into a record type.

        :param dictIn: The JSON dict to convert
            into a record type

        :return: The record object corresponding
            to the input dict
        """
        pass


class Subject(Record):
    """
    A record type corresponding
    to a subject in the study
    planner.

    :param uid: The UID of this subject
    :param name: The name of this subject
    :param active: Whether or not this subject is "active". Allows
    us to remove subjects from consideration when scheduling.
    :param weight: A scalar we multiply by the raw
      fibonacci number prediction. This is then added with
      a bias term to get the final prediction.
    :param bias: A scalar representing a lag in days that we add
      to the weighted prediction. Allows us to push the prediction
      forward or backward in time.
    """

    def __init__(
        self, uid: UID, name: str, active: bool, weight: float = 1.0, bias: int = 0
    ) -> None:
        super().__init__(uid)
        self.name: str = name
        self.active: bool = active

        self.weight: float = weight
        self.bias: int = bias

    def toJSON(self) -> dict:
        """
        Converts this subject to a JSON dict.

        :return: A JSON dict where all the types
            in it are serializable by Python's
            native JSON module
        """

        return {
            "uid": self.uid.toString(),
            "name": self.name,
            "active": self.active,
            "weight": self.weight,
            "bias": self.bias,
            "type": "subject",
        }

    @staticmethod
    def fromJSON(dictIn: dict) -> "Subject":
        """
        Converts a JSON dict into a Subject object.

        :param dictIn: The JSON dict to convert
            into a record type

        :return: The subject object corresponding
            to the input dict
        """

        return Subject(
            uid=UID.fromString(dictIn["uid"]),
            name=dictIn["name"],
            active=dictIn["active"],
            weight=dictIn["weight"],
            bias=dictIn["bias"],
        )


# The default fib-number for new topics
NEW_TOPIC_DEFAULT_FIB: int = 2


class Topic(Record):
    """
    A record type corresponding to a Topic in our
    study planner. Topics belong to subjects, and these
    are the things that we actually study.

    :param uid: The UID of this topic
    :param name: The name of this topic
    :param subjectUID: The UID of the parent subject
    :param active: Whether or not this topic is "active". Allows
        us to remove topics from consideration when scheduling.
    :param dTime: If set, specifies the datetime of this topic.
        Otherwise, uses the current datetime
    :param fibNumber:
    """

    def __init__(
        self,
        uid: UID,
        name: str,
        subjectUID: UID,
        active: bool,
        fibNumber: int = NEW_TOPIC_DEFAULT_FIB,
        dTime: datetime = datetime.now(tz=timezone.utc),
    ) -> None:
        super().__init__(uid)
        self.name: str = name
        self.subjectUID: UID = subjectUID
        self.active: bool = active
        self.lastStudy: datetime = dTime
        self.fibNumber: int = fibNumber

    def toJSON(self) -> dict:
        """
        Converts this topic to a JSON dict.

        :return: A JSON dict where all the types
            in it are serializable by Python's
            native JSON module
        """

        return {
            "uid": self.uid.toString(),
            "name": self.name,
            "subjectUID": self.subjectUID.toString(),
            "active": self.active,
            "lastStudy": self.lastStudy.isoformat(),
            "fibNumber": self.fibNumber,
            "type": "topic",
        }

    @staticmethod
    def fromJSON(dictIn: dict) -> "Topic":
        """
        Converts a JSON dict into a Topic object.

        :param dictIn: The JSON dict to convert
            into a record type

        :return: The topic object corresponding
            to the input dict
        """

        return Topic(
            uid=UID.fromString(dictIn["uid"]),
            name=dictIn["name"],
            subjectUID=UID.fromString(dictIn["subjectUID"]),
            active=dictIn["active"],
            dTime=datetime.fromisoformat(dictIn["lastStudy"]),
            fibNumber=dictIn["fibNumber"],
        )


class Database:
    """
    A type representing the database. Contains
    a list of records. Allows general operations
    over records.
    """

    def __init__(self, records: List[Record]) -> None:
        self.recordDict: Dict[UID, Record] = {}
        for record in records:
            self.recordDict[record.uid] = record

    def toJSONDict(self) -> dict:
        """
        Converts the database to a dictionary that
        can be serialized by Python's native JSON
        module.

        :return: A JSON dict where all the types
            in it are serializable by Python's
            native JSON module
        """
        resultDict: Dict[str, dict] = {}

        for uid, record in self.recordDict.items():
            resultDict[uid.toString()] = record.toJSON()

        return resultDict

    @staticmethod
    def fromJSONDict(dictIn: dict) -> "Database":
        """
        Converts a JSON dict into a Database object.

        :param dictIn: The JSON dict to convert
            into a record type

        :return: The database object corresponding
            to the input dict
        """
        records: List[Record] = []

        for uidStr, recordDict in dictIn.items():
            assert "type" in recordDict, "Record does not have a type"
            recordType = recordDict["type"]
            if recordType == "subject":
                records.append(Subject.fromJSON(recordDict))
            elif recordType == "topic":
                records.append(Topic.fromJSON(recordDict))
            else:
                assert False, "Unknown record type"

        return Database(records)

    def dumpToFile(self, filePath: str) -> None:
        """
        Dumps the database to a file.

        :param filePath: The file to dump the database to
        """
        with open(filePath, "w") as f:
            json.dump(self.toJSONDict(), f)

    @staticmethod
    def loadFromFile(filePath: str) -> "Database":
        """
        Loads a database from a file.

        :param filePath: The file to load the database from
        """
        with open(filePath, "r") as f:
            return Database.fromJSONDict(json.load(f))

    def insert(self, record: Record) -> None:
        """
        Inserts a record into the database.

        :param record: The record to insert
        """
        assert record.uid not in self.recordDict, "Record already exists in database"
        self.recordDict[record.uid] = record

    def delete(self, uid: UID) -> None:
        """
        Deletes a record from the database.

        :param uid: The UID of the record to delete
        """
        assert uid in self.recordDict, "Record does not exist in database"
        del self.recordDict[uid]

    def get(self, uid: UID) -> Record:
        """
        Gets a record from the database.

        :param uid: The UID of the record to get
        """
        assert uid in self.recordDict, "Record does not exist in database"
        return self.recordDict[uid]

    def update(self, record: Record) -> None:
        """
        Updates a record in the database.

        :param record: The record to update
        """
        assert record.uid in self.recordDict, "Record does not exist in database"
        self.recordDict[record.uid] = record

    RECORD_TVAR = TypeVar("RECORD_TVAR", bound=Record)

    def query(
        self, queryTypes: List[Type[RECORD_TVAR]], query: Callable[[Record], bool]
    ) -> "Database":
        """
        Runs a query over the current database, returning a new database
        whose records are those that return a boolean true when passed
        through the query callable.
        """
        records = []
        for record in self.recordDict.values():
            if type(record) in queryTypes and query(record):
                records.append(record)

        return Database(records)
