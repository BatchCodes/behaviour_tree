#! /usr/bin/env /python3

from abc import abstractmethod
from enum import Enum
from time import sleep
from datetime import datetime


class Status(Enum):
  READY = "READY"
  BUSY = "BUSY"


class LeafNode:
  status = Status.READY
  outcome = True

  @abstractmethod
  def __call__(self):
    return self.outcome, self.status


class BranchNode(LeafNode):
  def __init__(self, children=[]):
    self.children = children

  def addChild(self, child):
    self.children.append(child)

  def addChildren(self, children):
    self.children += children


class Condition(LeafNode):
  def __init__(self, evaluate=None):
    self._evaluate = evaluate

  def evaluate(self) -> bool:
    if self._evaluate is not None:
      return self._evaluate()

  def __call__(self):
    self.outcome = self.evaluate()
    return self.outcome, self.status


class Action(LeafNode):
  def __init__(self, execute):
    self._execute = execute

  def execute(self) -> bool:
    if self._execute is not None:
      return self._execute()

  def __call__(self, *args, **kwargs):
    if self.status == Status.READY:
      self.status = Status.BUSY
      self.outcome = self.execute()
      self.status = Status.READY
    return self.outcome, self.status


class Sequence(BranchNode):
  def __call__(self):
    self.outcome = True
    for child in self.children:
      outcome, self.status = child()

      if self.status == Status.BUSY:
        break

      self.outcome = self.outcome and outcome
      if not self.outcome:
        break
    return self.outcome, self.status


class Fallback(BranchNode):
  def __call__(self):
    self.outcome = False
    for child in self.children:
      outcome, self.status = child()

      if self.status == Status.BUSY:
        break

      self.outcome = self.outcome or outcome
      if self.outcome:
        break
    return self.outcome, self.status


class Blackboard():
  def __init__(self, innerDict=None):
    self.innerDict = innerDict or dict()
    self.locked = False

  def __enter__(self):
    self.locked = True

  def __exit__(self, exceptionType, value, traceback):
    self.locked = False

  def __getitem__(self, key):
    while self.locked:
      sleep(0.1)

    with self:
      if key not in self.innerDict:
        return None
      return self.innerDict[key]

  def __setitem__(self, key, value):
    while self.locked:
      sleep(0.1)

    with self:
      self.innerDict[key] = value

  def __iter__(self):
    return iter(self.innerDict)


class BehaviourTree:
  def __init__(self, blackboard=None, children=[],  rate=1):
    self.blackboard = blackboard or Blackboard()
    self.children = children
    self.rate = rate

  def run(self):
    while True:
      tick = datetime.timestamp(datetime.now())
      for child in self.children:
        _, status = child()
        if status == Status.BUSY:
          break
      tock = datetime.timestamp(datetime.now())
      if (tock - tick) > (1/self.rate):
        print("Takes to long for rate")
        continue
      sleep((1/self.rate) - (tock-tick))

  def runOnce(self):
    for child in child():
      child()

  def Action(self, func, passBlackboard=True):
    execute = (
        lambda: func(self.blackboard)
        if passBlackboard
        else func
    )
    return Action(execute=execute)

  def Condition(self, func, passBlackboard=True):
    evaluate = (
        lambda: func(self.blackboard)
        if passBlackboard
        else func
    )
    return Condition(evaluate=evaluate)

  def Sequence(self, *children):
    if len(children) == 1 and isinstance(children[0], list):
      children = children[0]
    if isinstance(children, tuple):
      children = list(children)
    return Sequence(children)

  def Fallback(self, *children):
    if len(children) == 1 and isinstance(children[0], list):
      children = children[0]
    if isinstance(children, tuple):
      children = list(children)
    return Fallback(children)

  def setTree(self, *children):
    if len(children) == 1 and isinstance(children[0], list):
      children = children[0]
    if isinstance(children, tuple):
      children = list(children)
    self.children = children

  def setBlackboard(self, blackboard):
    if isinstance(blackboard, Blackboard):
      self.blackboard = blackboard
      return

    if isinstance(blackboard, dict):
      self.blackboard = Blackboard(blackboard)
      return

    raise TypeError(
        "Blackboard must be of type dict or behaviour_trees.Blackboard"
    )
