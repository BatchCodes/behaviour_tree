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
  def evaluate(self):
    return self.blackboard["HAS_BALL"]


class GetBall(Action):
  def execute(self):
    print("Getting Ball")
    self.blackboard["HAS_BALL"] = True
    self.blackboard["AT_WALL"] = False
    return True


class AtWall(Condition):
  def evaluate(self):
    return self.blackboard["AT_WALL"]


class MoveToWall(Action):
  def execute(self):
    print("Moving To Wall")
    self.blackboard["AT_WALL"] = True
    return True


class Play(Action):
  def execute(self):
    print("Playing")
    if random() < 0.3:
      print("LOST BALL")
      self.blackboard["HAS_BALL"] = False
      return True


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
