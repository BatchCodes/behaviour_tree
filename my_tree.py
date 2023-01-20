#! /usr/env/bin python3

from random import random
from behaviour_trees import (
    Blackboard,
    Root,
    Sequence,
    Fallback,
    Condition,
    Action,
)


class HasBall(Condition):
  def __bool__(self):
    hasBall = self.blackboard["HAS_BALL"]
    return hasBall


class GetBall(Action):
  def __call__(self):
    self.status = False
    print("Getting Ball")
    self.blackboard["HAS_BALL"] = True
    self.blackboard["AT_WALL"] = False
    self.status = True


class AtWall(Condition):
  def __bool__(self):
    atWall = self.blackboard["AT_WALL"]
    return atWall


class MoveToWall(Action):
  def __call__(self):
    self.status = False
    print("Moving To Wall")
    self.blackboard["AT_WALL"] = True
    self.status = True


class Play(Action):
  def __call__(self):
    self.status = False
    print("Playing")
    if random() < 0.3:
      print("LOST BALL")
      self.blackboard["HAS_BALL"] = False
    self.status = True


blackboard = Blackboard({
    "HAS_BALL": False,
    "AT_WALL": False
})

ballTree = Fallback(
    blackboard,
    [
        HasBall(blackboard),
        GetBall(blackboard)
    ]
)
wallTree = Fallback(
    blackboard,
    [
        AtWall(blackboard),
        MoveToWall(blackboard)
    ]
)

root = Root(
    rate=1,
    blackboard=blackboard,
    children=[
        Sequence(
            blackboard=blackboard,
            children=[
                ballTree,
                wallTree,
                Play(blackboard),
            ])
    ]
)

if __name__ == "__main__":
  root.run()
