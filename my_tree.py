#! /usr/env/bin python3

from random import random
from behaviour_trees import BehaviourTree


def hasBall(blackboard):
  return blackboard["HAS_BALL"]


def getBall(blackboard):
  print("Getting Ball")
  blackboard["HAS_BALL"] = True
  blackboard["AT_WALL"] = False
  return True


def atWall(blackboard):
  return blackboard["AT_WALL"]


def moveToWall(blackboard):
  print("Moving To Wall")
  blackboard["AT_WALL"] = True
  return True


def play(blackboard):
  print("Playing")
  if random() < 0.3:
    print("LOST BALL")
    blackboard["HAS_BALL"] = False
    return False
  return True


bh = BehaviourTree({
    "HAS_BALL": False,
    "AT_WALL": False
})
ballTree = bh.Fallback(
    bh.Condition(hasBall),
    bh.Action(getBall)
)

wallTree = bh.Fallback(
    bh.Condition(atWall),
    bh.Action(moveToWall)
)

bh.setTree(
    bh.Sequence(
        ballTree,
        wallTree,
        bh.Action(play)
    )
)

if __name__ == "__main__":
  bh.run()
