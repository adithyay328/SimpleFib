"""Implements CLI"""
import os

from simplepycli import PyCLIApp
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator
from prompt_toolkit.completion import FuzzyWordCompleter

from simplefib.validators import *
from simplefib.db import *
from simplefib.uid import UID

app: PyCLIApp = PyCLIApp("> ")

# File name where DB is dumped to
DB_DUMP_FNAME: str = "db.json"

# Loading up or creating a DB
db = (
    Database([])
    if DB_DUMP_FNAME not in os.listdir()
    else Database.loadFromFile(DB_DUMP_FNAME)
)


# Create new subjects
@app.command("create_subject", "Creates a new subject in the study planner")
def createSubject(params) -> None:
    subjectName: str = prompt("Please type in a subject name to create: ")

    subjWeight: float = float(
        prompt(
            "Please type in a subject weight for this subject. ",
            default="2.5",
            validator=Validator.from_callable(
                validateFloat, error_message="Input should be a floating point."
            ),
        )
    )

    subjBias: int = int(
        prompt(
            "Please type in a subject bias for this subject. ",
            default="0",
            validator=Validator.from_callable(
                validateInt, error_message="Input should be an integer."
            ),
        )
    )

    # Constructing the subject
    newSubject: Subject = Subject(UID(), subjectName, True, subjWeight, subjBias)

    # Add to the DB
    db.insert(newSubject)


@app.command("list_subjects", "Lists all the subjects in the study planner")
def listSubjects(params) -> None:
    for record in db.recordDict.values():
        if type(record) != Subject:
            continue

        print(f"Subject: {record.name}, Weight: {record.weight}, Bias: {record.bias}")

def subjectNamePrompt():
    """
    A helper function to prompt for subject names.
    """
    subjectNames: List[str] = getSubjectNames(db)
    subjectCompleter: FuzzyWordCompleter = FuzzyWordCompleter(subjectNames)
    subjectValidator: Validator = Validator.from_callable(
        getSubjectNameValidator(db),
        error_message="Input should be a valid subject name.",
    )
    subjectName: str = prompt(
        "Please type in the name of the subject this topic belongs to: ",
        validator=subjectValidator,
        completer=subjectCompleter,
    )
    
    return subjectName

@app.command("create_topic", "Creates a new topic in the study planner")
def createTopic(params) -> None:
    topicName: str = prompt("Please type in a topic name to create: ")

    subjectName: str = subjectNamePrompt()

    # Get UID from subject name
    subjUID: str = ""
    for record in db.recordDict.values():
        if type(record) == Subject:
            if record.name == subjectName:
                subjUID += record.uid.uid

    # Constructing the topic
    newTopic: Topic = Topic(UID(), topicName, UID(subjUID), True)

    # Add to the DB
    db.insert(newTopic)

@app.command("complete_task", "Completes a text, incrementing its fib count by 1")
def completeTask(params):
    """
    Allows users to complete tasks, specifying subject first and then the topic number.
    """
    # First, pick a subject name.
    subjectName: str = subjectNamePrompt()

    # Get UID from subject name
    subjUID: str = ""
    for record in db.recordDict.values():
        if type(record) == Subject:
            if record.name == subjectName:
                subjUID += record.uid.uid

    # Now, pick all topics from that subject
    allTopics : List[Topic] = []

    for record in db.recordDict.values():
        if type(record) == Topic and record.subjectUID.uid == subjUID:
            allTopics.append(record)
    
    # Now, build a validator and a completer for these topic
    # names
    selectedNamesCompleter : FuzzyWordCompleter = FuzzyWordCompleter([topic.name for topic in allTopics])
    selectedNamesValidator : Validator = Validator.from_callable(
        getStrListValidator([topic.name for topic in allTopics]),
        error_message="Input should be a valid topic name."
    )

    # Now, prompt for the topic name
    topicName : str = prompt(
        "Please type in the name of the topic you want to complete: ",
        validator=selectedNamesValidator,
        completer=selectedNamesCompleter
    )

    # Now, get the topic UID
    topicUID : str = ""
    for topic in allTopics:
        if topic.name == topicName:
            topicUID += topic.uid.uid
    
    # Now, get the topic from the DB
    topic : Record = db.get(UID(topicUID))
    assert type(topic) == Topic

    # Now, increase the fib count
    topic.fibNumber += 1

    # Update DB
    db.update(topic)

def run():
    app.run()

    # Save db to disk
    db.dumpToFile(DB_DUMP_FNAME)