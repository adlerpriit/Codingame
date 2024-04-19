package main

import (
	"fmt"
	"math"
	"os"
	"sort"
	"time"
)

type Point struct {
	x, y int
}

func (p Point) distance(p2 Point) int {
	// keep in mind that the distance is squared
	return (p.x-p2.x)*(p.x-p2.x) + (p.y-p2.y)*(p.y-p2.y)
}

func (p Point) angle(p2 Point) float64 {
	return abs_angle(math.Atan2(float64(p2.y-p.y), float64(p2.x-p.x)))
}

func (p Point) project(angle float64, d int) Point {
	return Point{p.x + int(math.Cos(angle)*float64(d)), p.y + int(math.Sin(angle)*float64(d))}
}

type Pod struct {
	id               int
	position         Point
	vx, vy           int
	angle            float64 // this is in radians
	nextCheckPointId int
	radius           int
}

func (p Pod) adjust_speed(checkpoints []CP, target Point, debug bool) int {
	speed_angle_t := normalize_angle(p.position.angle(target) - p.angle)
	speed_angle_f := normalize_angle(p.position.angle(checkpoints[p.nextCheckPointId%len(checkpoints)].position) - p.angle)
	speed_angle_v := normalize_angle(p.position.angle(checkpoints[p.nextCheckPointId%len(checkpoints)].position) - Point{0, 0}.angle(Point{p.vx, p.vy}))
	inv_speed := (2*speed_angle_t*speed_angle_t + 4*speed_angle_f*speed_angle_f + speed_angle_v*speed_angle_v) * 5
	if debug {
		fmt.Fprintln(os.Stderr, speed_angle_f, speed_angle_v, inv_speed)
	}
	if inv_speed >= 200 {
		return 0
	}
	return int(200 - inv_speed)
}

func (p Pod) adjust_speed_defend(oPod Pod, target Point, debug bool) int {
	speed_angle_t := normalize_angle(p.position.angle(target) - p.angle)
	speed_angle_f := normalize_angle(p.position.angle(oPod.position) - p.angle)
	speed_angle_v := normalize_angle(p.position.angle(oPod.position) - Point{0, 0}.angle(Point{p.vx, p.vy}))
	inv_speed := (2*speed_angle_t*speed_angle_t + 4*speed_angle_f*speed_angle_f + speed_angle_v*speed_angle_v) * 5
	if debug {
		fmt.Fprintln(os.Stderr, speed_angle_f, speed_angle_v, inv_speed)
	}
	if inv_speed >= 200 {
		return 0
	}
	return int(200 - inv_speed)
}

func (p Pod) predict_action(checkpoints []CP, pods []Pod) string {
	// new plan, split map into POIs and predict pod trajectory toward each POI
	// other pods are with the aim of predicting collisions and take them into account when projecting turns ahead
	cpid := p.nextCheckPointId
	d2cp := p.position.distance(checkpoints[cpid].position)
	POI := checkpoints[cpid].position
	// trajectory := make([]Pod, 20)
	for x := -4; x < 20; x++ {
		for y := -3; y < 12; y++ {
			target := Point{x * 1000, y * 1000}
			pod := p
			// pods := make([]Pod, 20)
			for i := 0; i < 15; i++ {
				delta_angle := cap_angle(normalize_angle(pod.position.angle(target) - pod.angle))
				// adjust thrust based on next checkpoint and target
				thrust := pod.adjust_speed(checkpoints, target, false)
				pod = pod.next_position(thrust, delta_angle, checkpoints)
				if i < 5 {
					// other pod movement is generic
					// only do collision detection in less than 5 turns prediction (cause it's highly unreliable)
					for _, other_pod := range pods {
						if other_pod.id == pod.id {
							continue
						}
						for t := 0; t <= i; t++ {
							other_pod = other_pod.next_position(150, 0, checkpoints)
						}
						collide, t := pod.willCollide(other_pod)
						if collide && t < 1 {
							// fmt.Fprintln(os.Stderr, "Collision with opponent at t: ", t, "opod: ", other_pod.id, "turn:", i)
							// this is highly unreliable and the purpose here is to disrupt normal trajectory calculation
							new_vx, new_vy := pod.resolveCollision(other_pod)
							// don't bother to accurately calculate new position after collision, just assign new vx and vy for direction change
							pod.vx = new_vx
							pod.vy = new_vy
						}
					}
				}
				// pods[i] = pod
			}
			if pod.nextCheckPointId > cpid {
				cpid = pod.nextCheckPointId
				d2cp = pod.position.distance(checkpoints[cpid%len(checkpoints)].position)
				POI = target
				// trajectory = pods
			}
			if pod.nextCheckPointId == cpid && pod.position.distance(checkpoints[cpid%len(checkpoints)].position) < d2cp {
				d2cp = pod.position.distance(checkpoints[cpid%len(checkpoints)].position)
				POI = target
				// trajectory = pods
			}
		}
	}
	fmt.Fprintln(os.Stderr, "POI: ", POI, "d2cp: ", d2cp, "cpid: ", cpid, int(p.angle/math.Pi*180))
	// for _, pod := range trajectory {
	// 	fmt.Fprintln(os.Stderr, pod.position, int(pod.angle/math.Pi*180),
	// 		"turn: ", int(pod.position.angle(POI)/math.Pi*180),
	// 		"ncpid: ", pod.nextCheckPointId)
	// }

	// check if we are going to collide with opponent
	for _, opod := range pods[2:] {
		collide, t := p.willCollide(opod)
		if collide && t < 1 {
			// we are going to collide, let's report it
			fmt.Fprintln(os.Stderr, "Collision with opponent at t: ", t, "opod: ", opod.id)
			// if velocity angles are opposite, apply shield
			if math.Abs(normalize_angle(p.angle-opod.angle)) > math.Pi/5 {
				return fmt.Sprintf("%d %d SHIELD", POI.x, POI.y)
			}
		}
	}

	thrust := p.adjust_speed(checkpoints, POI, false)
	return fmt.Sprintf("%d %d %d", POI.x, POI.y, thrust)
}

func get_defend_score(p Pod, checkpoints []CP) float64 {
	angle_f := math.Abs(normalize_angle(p.position.angle(checkpoints[p.nextCheckPointId%len(checkpoints)].position) - p.angle))
	angle_v := math.Abs(normalize_angle(p.position.angle(checkpoints[p.nextCheckPointId%len(checkpoints)].position) - Point{0, 0}.angle(Point{p.vx, p.vy})))
	speed := Point{0, 0}.distance(Point{p.vx, p.vy})
	return angle_f * angle_v * float64(speed)

}

func (p Pod) defend_action(checkpoints []CP, pods []Pod, oLead int) string {
	// function to block opponent lead pod, need to figure out how to intercept him the best
	// assumption is that we know the order of pods ranking
	// call this function if I'm not leading and this pod is the second one of mine
	// try to target the lead opponent pod and optimise for his facing angle, velocity angle and speed relative to his next checkpoint
	tPod := pods[oLead]
	score := get_defend_score(tPod, checkpoints)
	POI := checkpoints[(tPod.nextCheckPointId+1)%len(checkpoints)].position
	// trajectory := make([]Pod, 20)
	for x := -4; x < 20; x++ {
		for y := -3; y < 12; y++ {
			target := Point{x * 1000, y * 1000}
			pod := p
			// pods := make([]Pod, 20)
			hitTarget := false
			for i := 0; i < 10; i++ {
				delta_angle := cap_angle(normalize_angle(pod.position.angle(target) - pod.angle))
				// adjust thrust based on next checkpoint and target
				thrust := pod.adjust_speed_defend(tPod, target, false)
				pod = pod.next_position(thrust, delta_angle, checkpoints)
				if i < 10 {
					// other pod movement is generic
					// only do collision detection in less than 5 turns prediction (cause it's highly unreliable)
					for _, other_pod := range pods {
						if other_pod.id == pod.id {
							continue
						}
						for t := 0; t <= i; t++ {
							other_pod = other_pod.next_position(150, 0, checkpoints)
						}
						collide, t := pod.willCollide(other_pod)
						if collide && t < 1 {
							// fmt.Fprintln(os.Stderr, "Collision with opponent at t: ", t, "opod: ", other_pod.id, "turn:", i)
							// this is highly unreliable and the purpose here is to disrupt normal trajectory calculation
							if other_pod.id == tPod.id {
								hitTarget = true
								// if hitting the target, resolve collision with him and predict movement for one more turn, though it is not accurate
								new_vx, new_vy := other_pod.resolveCollision(pod)
								pod.vx = new_vx
								pod.vy = new_vy
								other_pod = other_pod.next_position(150, 0, checkpoints)
								if score < get_defend_score(other_pod, checkpoints) {
									score = get_defend_score(other_pod, checkpoints)
									POI = target
								}
							} else {
								new_vx, new_vy := pod.resolveCollision(other_pod)
								// don't bother to accurately calculate new position after collision, just assign new vx and vy for direction change
								pod.vx = new_vx
								pod.vy = new_vy
							}
						}
					}
				}
				if hitTarget {
					break
				}
			}
		}
	}

	// check if we are going to collide with opponent
	for _, opod := range pods[2:] {
		collide, t := p.willCollide(opod)
		if collide && t < 1 {
			// we are going to collide, let's report it
			fmt.Fprintln(os.Stderr, "Collision with opponent at t: ", t, "opod: ", opod.id)
			// if velocity angles are opposite, apply shield
			if math.Abs(normalize_angle(p.angle-opod.angle)) > math.Pi/3 {
				return fmt.Sprintf("%d %d SHIELD", POI.x, POI.y)
			}
		}
	}

	thrust := p.adjust_speed_defend(tPod, POI, false)
	return fmt.Sprintf("%d %d %d", POI.x, POI.y, thrust)
}

// Predicts if and when two pods will collide
func (p Pod) willCollide(p2 Pod) (bool, float64) {
	dx := p2.position.x - p.position.x
	dy := p2.position.y - p.position.y
	// assume speed preserving thrust
	vx := int(float64(p2.vx-p.vx) / 0.85)
	vy := int(float64(p2.vy-p.vy) / 0.85)

	// Coefficients for the quadratic equation (At^2 + Bt + C = 0)
	A := vx*vx + vy*vy
	B := 2 * (dx*vx + dy*vy)
	C := dx*dx + dy*dy - int(float64(p.radius+p2.radius)*float64(p.radius+p2.radius))

	if A == 0 { // Check if the pods are moving parallel
		return false, 0
	}

	discriminant := B*B - 4*A*C
	if discriminant < 0 {
		return false, 0 // No collision
	}

	t := (float64(-B) - math.Sqrt(float64(discriminant))) / (2 * float64(A))
	if t < 0 {
		return false, 0 // Collision is in the past
	}

	return true, t // Collision time
}

func (p Pod) resolveCollision(p2 Pod) (int, int) {
	// Calculate the difference in position
	dx := float64(p2.position.x - p.position.x)
	dy := float64(p2.position.y - p.position.y)

	// Calculate the distance between two pods
	distance := math.Sqrt(dx*dx + dy*dy)

	// Normalize the difference vector
	nx := dx / distance
	ny := dy / distance

	// Calculate the difference in velocities
	dvx := float64(p.vx - p2.vx)
	dvy := float64(p.vy - p2.vy)

	// Calculate the velocity along the normal (dot product)
	dot := dvx*nx + dvy*ny

	// Calculate the magnitude of the impulse along the normal
	impulse := 2 * dot / 2.0 // divided by 2 because we assume equal mass and we distribute the impulse evenly

	// Calculate the components of the impulse for each Pod
	impulseX := impulse * nx
	impulseY := impulse * ny

	// Update velocities by applying the impulse (pods exchange velocity along the line of impact)
	new_vx := p.vx - int(impulseX)
	new_vy := p.vy - int(impulseY)
	return new_vx, new_vy
}

func (p Pod) default_action(checkpoints []CP) string {
	return fmt.Sprintf("%d %d %s", checkpoints[p.nextCheckPointId].position.x, checkpoints[p.nextCheckPointId].position.y, "BOOST")
}

func (p Pod) next_position(thrust int, angle float64, checkpoints []CP) Pod {
	// angle here is the measure of additional facing change, pod angle is in radians
	// new angle is new facing angle
	new_angle := abs_angle(p.angle + angle)
	new_vx := p.vx + int(float64(thrust)*math.Cos(new_angle))
	new_vy := p.vy + int(float64(thrust)*math.Sin(new_angle))
	new_x := p.position.x + new_vx
	new_y := p.position.y + new_vy
	new_vx = int(0.85 * float64(new_vx))
	new_vy = int(0.85 * float64(new_vy))
	new_nextCheckPointId := p.nextCheckPointId
	// check if we passed the checkpoint
	if pass_CP(checkpoints[p.nextCheckPointId%len(checkpoints)], p.position, Point{new_x, new_y}) {
		new_nextCheckPointId = (p.nextCheckPointId + 1)
	}
	return Pod{p.id, Point{new_x, new_y}, new_vx, new_vy, new_angle, new_nextCheckPointId, p.radius}
}

type CP struct {
	position Point
	radius   int
}

func pass_CP(checkpoint CP, P, d Point) bool {
	// Line vector
	ax := d.x - P.x
	ay := d.y - P.y

	// Vector from A to P
	bx := checkpoint.position.x - P.x
	by := checkpoint.position.y - P.y

	// Project vector AP onto AB
	dotProduct := bx*ax + by*ay
	lenSq := ax*ax + ay*ay
	if lenSq == 0 {
		// we are not moving
		return false
	}
	param := dotProduct / lenSq

	// Find the closest point on the line
	cx, cy := P.x+ax*param, P.y+ay*param

	if param < 0.0 || (P.x == d.x && P.y == d.y) {
		cx, cy = P.x, P.y
	} else if param > 1.0 {
		cx, cy = d.x, d.y
	}

	// did we pass through checkpoint during this move?
	return checkpoint.position.distance(Point{cx, cy}) < checkpoint.radius*checkpoint.radius-400
}

func normalize_angle(angle float64) float64 {
	// keep angle between -pi and pi
	if angle > math.Pi {
		return angle - 2*math.Pi
	}
	if angle < -math.Pi {
		return angle + 2*math.Pi
	}
	return angle
}

func abs_angle(angle float64) float64 {
	// keep angle between 0 and 2*pi
	if angle < 0 {
		return angle + 2*math.Pi
	}
	return angle
}

func cap_angle(angle float64) float64 {
	// cap angle to 18 degrees
	if angle > math.Pi/10 {
		return math.Pi / 10
	}
	if angle < -math.Pi/10 {
		return -math.Pi / 10
	}
	return angle
}

type Rank struct {
	id           int
	lap          int
	checkPointId int
	d2cp         int
}

func main() {
	var laps int
	fmt.Scan(&laps)

	var checkpointCount int
	fmt.Scan(&checkpointCount)
	var checkpoints = make([]CP, checkpointCount)

	for i := 0; i < checkpointCount; i++ {
		var checkpointX, checkpointY int
		fmt.Scan(&checkpointX, &checkpointY)
		checkpoints[i] = CP{Point{checkpointX, checkpointY}, 600}
	}
	TURN := 0
	RANK := make([]Rank, 4)
	for i := 0; i < 4; i++ {
		RANK[i] = Rank{i, 0, 1, 0}
	}
	for {
		start := time.Now()
		pods := make([]Pod, 4)
		for i := 0; i < 4; i++ {
			// two first ones are mine, two last ones are opponent
			// x: x position of your pod
			// y: y position of your pod
			// vx: x speed of your pod
			// vy: y speed of your pod
			// angle: angle of your pod
			// nextCheckPointId: next check point id of your pod
			var x, y, vx, vy, angle, nextCheckPointId int
			fmt.Scan(&x, &y, &vx, &vy, &angle, &nextCheckPointId)
			var rad_angle float64
			if angle == -1 {
				rad_angle = abs_angle(Point{x, y}.angle(checkpoints[nextCheckPointId].position))
			} else {
				rad_angle = float64(angle) * math.Pi / 180
			}
			pods[i] = Pod{i + 1, Point{x, y}, vx, vy, rad_angle, nextCheckPointId, 400}
			RANK[i].d2cp = pods[i].position.distance(checkpoints[nextCheckPointId].position) // the distance is squared
			if nextCheckPointId != RANK[i].checkPointId {
				RANK[i].checkPointId = nextCheckPointId
				if nextCheckPointId == 0 {
					RANK[i].lap += 1
				}
			}
		}

		// fmt.Fprintln(os.Stderr, "Debug messages...")
		for _, r := range RANK {
			fmt.Fprintln(os.Stderr, r)
		}
		RANK_SORT := make([]Rank, 4)
		copy(RANK_SORT, RANK)
		sort.Slice(RANK_SORT, func(a, b int) bool {
			if RANK_SORT[a].lap == RANK_SORT[b].lap {
				if RANK_SORT[a].checkPointId == RANK_SORT[b].checkPointId {
					return RANK_SORT[a].d2cp < RANK_SORT[b].d2cp
				}
				return RANK_SORT[a].checkPointId > RANK_SORT[b].checkPointId
			}
			return RANK_SORT[a].lap > RANK_SORT[b].lap
		})
		// oLead := 0
		// for _, r := range RANK_SORT {
		// 	if r.id > 1 {
		// 		oLead = r.id
		// 		break
		// 	}
		// }

		if TURN == 0 {
			fmt.Println(pods[0].default_action(checkpoints))
		} else {
			fmt.Println(pods[0].predict_action(checkpoints, pods))
		}

		fmt.Println(pods[1].predict_action(checkpoints, pods))

		elapsed := time.Since(start)
		fmt.Fprintln(os.Stderr, "Elapsed time: ", elapsed.Seconds())
		TURN++
	}
}
