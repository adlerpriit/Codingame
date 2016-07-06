import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


# game loop
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    x, y, next_x, next_y, next_dist, angle = [int(i) for i in input().split()]
    o_x, o_y = [int(i) for i in input().split()]

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    #thrust equals abs(angls)
    print([next_dist,angle],file=sys.stderr)

    dist_limit = 0

    if next_dist < 1000:
        #max limit 30
        dist_limit = int((next_dist * 30) / 1000)

    thrust = int(100 - abs(angle/3))

    # You have to output the target position
    # followed by the power (0 <= thrust <= 100)
    # i.e.: "x y thrust"
    print(str(next_x) + " " + str(next_y) + " " + str(thrust))
