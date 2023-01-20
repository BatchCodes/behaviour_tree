#! /usr/env/bin /python3

from abc import abstractmethod
from enum import Enum
from time import sleep
from datetime import datetime


class Status(Enum):
  READY = "READY"
  BUSY = "BUSY"


class TreeNode:
  def __init__(self, blackboard):
    self.blackboard = blackboard
    self.status = Status.READY
    self.outcome = True

  @abstractmethod
  def __bool__(self):
    pass

  def __call__(self):
    return self.outcome, self.status


class BranchNode(TreeNode):
  def __init__(self, blackboard, children=[]):
    super().__init__(blackboard)
    self.children = children

  def addChild(self, child):
    self.children.append(child)

  def addChildren(self, children):
    self.children += children


class LeafNode(TreeNode):
  pass


class Condition(LeafNode):
  @abstractmethod
  def evaluate(self) -> bool:
    pass

  def __call__(self):
    self.outcome = self.evaluate()
    return self.outcome, self.status


class Action(LeafNode):
  @abstractmethod
  def execute(self) -> bool:
    pass

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


class Root(BranchNode):
  def __init__(self, rate, children=[], blackboard=None):
    self.rate = rate
    self.children = children
    self.blackboard = blackboard or Blackboard()

  def run(self):
    while True:
      tick = datetime.timestamp(datetime.now())
      for child in self.children:
        outcome, status = child()
      tock = datetime.timestamp(datetime.now())
      if (tock - tick) > (1/self.rate):
        print("Takes to long for rate")
        continue
      sleep((1/self.rate) - (tock-tick))

  def __get__(self, key):
    if key not in self.blackboard:
      return None
    return self.blackboard[key]

  def __set__(self, key, value):
    self.blackboard[key] = value
