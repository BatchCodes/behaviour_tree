#! /usr/env/bin /python3

from abc import abstractmethod
from time import sleep
from datetime import datetime


class TreeNode:
  def __init__(self, blackboard):
    self.blackboard = blackboard

  @abstractmethod
  def __bool__(self):
    pass


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
  def __bool__(self):
    pass


class Action(LeafNode):
  status = None

  @abstractmethod
  def __call__(self, *args, **kwargs):
    pass

  @abstractmethod
  def __bool__(self):
    self()
    return self.status


class Sequence(BranchNode):
  def __bool__(self):
    for child in self.children:
      if not bool(child):
        return False
    return True


class Fallback(BranchNode):
  def __bool__(self):
    for child in self.children:
      if bool(child):
        return True
    return False


class Blackboard():
  def __init__(self, innerDict=None):
    self.innerDict = innerDict or None

  def __getitem__(self, key):
    if key not in self.innerDict:
      return None
    return self.innerDict[key]

  def __setitem__(self, key, value):
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
        bool(child)
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
