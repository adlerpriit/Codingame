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
	angle_delta      float64
	nextCheckPointId int
	radius           int
	lastCP           bool
	rank             int
	shield           int
}

func (p Pod) adjust_speed(reference Point, target Point, debug bool) int {
	speed_angle_t := normalize_angle(p.position.angle(target) - p.angle)
	speed_angle_f := normalize_angle(p.position.angle(reference) - p.angle)
	speed_angle_v := normalize_angle(p.position.angle(reference) - Point{0, 0}.angle(Point{p.vx, p.vy}))
	inv_speed := (3*speed_angle_t*speed_angle_t + 2*speed_angle_f*speed_angle_f + speed_angle_v*speed_angle_v) * 5
	if debug {
		fmt.Fprintln(os.Stderr, speed_angle_f, speed_angle_v, inv_speed)
	}
	if inv_speed >= 200 || p.shield > 0 {
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
	for x := -4; x < 20; x++ {
		for y := -3; y < 12; y++ {
			target := Point{x * 1000, y * 1000}
			allPods := make([]Pod, 4)
			copy(allPods, pods)
			for i := 0; i < 15; i++ {
				for pid, apod := range allPods {
					delta_angle := apod.angle_delta
					// adjust thrust based on next checkpoint and target
					thrust := 190
					if apod.id == p.id {
						delta_angle = cap_angle(normalize_angle(apod.position.angle(target) - apod.angle))
						thrust = p.adjust_speed(checkpoints[apod.nextCheckPointId%len(checkpoints)].position, target, false)
					}
					allPods[pid] = apod.next_position(thrust, delta_angle, checkpoints)
					if apod.id == p.id {
						continue
					}
					collide, t := allPods[p.id].willCollide(apod)
					if collide && t < 1 {
						// this is highly unreliable and the purpose here is to disrupt normal trajectory calculation
						pvx, pvy, p2vx, p2vy := allPods[p.id].resolveCollision(apod)
						// don't bother to accurately calculate new position after collision, just assign new vx and vy for direction change
						allPods[p.id].vx = pvx
						allPods[p.id].vy = pvy
						allPods[pid].vx = p2vx
						allPods[pid].vy = p2vy
					}
				}
				if p.lastCP && allPods[p.id].nextCheckPointId > cpid {
					d2cp = 15 - i
					POI = target
					break
				}
			}
			if !p.lastCP && allPods[p.id].nextCheckPointId > cpid {
				cpid = allPods[p.id].nextCheckPointId
				d2cp = allPods[p.id].position.distance(checkpoints[cpid%len(checkpoints)].position)
				POI = target
			}
			if allPods[p.id].nextCheckPointId == cpid && allPods[p.id].position.distance(checkpoints[cpid%len(checkpoints)].position) < d2cp {
				d2cp = allPods[p.id].position.distance(checkpoints[cpid%len(checkpoints)].position)
				POI = target
			}
		}
	}
	speed := math.Round(math.Sqrt(float64(Point{0, 0}.distance(Point{p.vx, p.vy})) / 0.85))
	fmt.Fprintln(os.Stderr, "POI: ", POI, "d2cp: ", d2cp, "cpid: ", cpid, "speed: ", speed, "lastCP: ", p.lastCP, int(p.angle/math.Pi*180))
	// check if we are going to collide with opponent
	for _, opod := range pods[2:] {
		collide, t := p.willCollide(opod)
		if collide && t < 1 {
			// we are going to collide, let's report it
			fmt.Fprintln(os.Stderr, "Collision with opponent at t: ", t, "opod: ", opod.id)
			// if velocity angles are opposite, apply shield
			if (math.Abs(normalize_angle(p.angle-opod.angle)) > math.Pi/5 &&
				Point{0, 0}.distance(Point{p.vx, p.vy}) > 100*200) {
				pods[p.id].shield = 3
				return fmt.Sprintf("%d %d SHIELD", POI.x, POI.y)
			}
		}
	}
	thrust := p.adjust_speed(checkpoints[p.nextCheckPointId].position, POI, false)
	return fmt.Sprintf("%d %d %d", POI.x, POI.y, thrust)
}

func (p Pod) defend_action(checkpoints []CP, pods []Pod) string {
	// try to collide with opponent lead (head on)
	// if no collision, move toward center of the map
	// if within distance of 3000 units from map center, turn off thrust and pivot towards opponent lead
	// first find leading opponent
	t_pod := pods[2]
	if pods[2].rank > pods[3].rank {
		t_pod = pods[3]
	}
	POI := t_pod.position.project(t_pod.angle, 1000)
	t_turn := 10
	t_angle := 0.0
	// find best collision solution against opponent targeted pod
	for x := -4; x < 20; x++ {
		for y := -3; y < 12; y++ {
			target := Point{x * 1000, y * 1000}
			pod := p
			for i := 0; i < 8; i++ {
				// other pod movement is generic
				// only do collision detection in less than 5 turns prediction (cause it's highly unreliable)
				t_collide := false
				t_collide_pod := Pod{}
				for _, other_pod := range pods {
					if other_pod.id == pod.id {
						continue
					}
					for t := 0; t < i; t++ {
						other_pod = other_pod.next_position(190, 0, checkpoints)
					}
					collide, t := pod.willCollide(other_pod)
					if collide && t < 1 {
						// this is highly unreliable and the purpose here is to disrupt normal trajectory calculation
						pod.resolveCollision(other_pod)
						// don't bother to accurately calculate new position after collision, just assign new vx and vy for direction change
						if other_pod.id == t_pod.id {
							t_collide = true
							t_collide_pod = other_pod
						}
					}
				}
				if t_collide {
					// we have collision with target
					if math.Abs(normalize_angle(pod.angle-t_collide_pod.angle)) > t_angle {
						t_angle = math.Abs(normalize_angle(pod.angle - t_collide_pod.angle))
						t_turn = i
						POI = target
						break
					}
				}
				delta_angle := cap_angle(normalize_angle(pod.position.angle(target) - pod.angle))
				// adjust thrust based on next checkpoint and target
				thrust := pod.adjust_speed(t_pod.position, target, false)
				pod = pod.next_position(thrust, delta_angle, checkpoints)
			}
		}
	}
	if t_turn < 10 && t_angle > math.Pi*0.6 {
		// we have collision solution
		fmt.Fprintln(os.Stderr, "expect collision in ", t_turn, " turns")
		if t_turn < 2 {
			// if velocity angles are opposite, apply shield
			return fmt.Sprintf("%d %d SHIELD", POI.x, POI.y)
		}
		thrust := p.adjust_speed(t_pod.position, POI, false)
		return fmt.Sprintf("%d %d %d", POI.x, POI.y, thrust)
	}
	center_point := Point{8000, 4500}
	if p.position.distance(center_point) < 2000*2000 {
		POI = t_pod.position.project(t_pod.angle, 1000)
		fmt.Fprintln(os.Stderr, "aiming leading opponent:", POI)
		return fmt.Sprintf("%d %d %d", POI.x, POI.y, 0)
	}
	thrust := p.adjust_speed(center_point, center_point, false)
	fmt.Fprintln(os.Stderr, "moving toward center")
	return fmt.Sprintf("%d %d %d", center_point.x, center_point.y, thrust)
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

func (p Pod) resolveCollision(p2 Pod) (int, int, int, int) {
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
	pvx := p.vx - int(impulseX)
	pvy := p.vy - int(impulseY)
	p2vx := p2.vx + int(impulseX)
	p2vy := p2.vy + int(impulseY)
	return pvx, pvy, p2vx, p2vy
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
	shield := p.shield
	if shield > 0 {
		shield -= 1
	}
	return Pod{
		id:               p.id,
		position:         Point{new_x, new_y},
		vx:               new_vx,
		vy:               new_vy,
		angle:            new_angle,
		nextCheckPointId: new_nextCheckPointId,
		radius:           p.radius,
		lastCP:           p.lastCP,
		shield:           shield}
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
	return checkpoint.position.distance(Point{cx, cy}) < checkpoint.radius*checkpoint.radius-900
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
	pods := make([]Pod, 4)
	for i := 0; i < 4; i++ {
		pods[i] = Pod{id: i, radius: 400}
	}
	for {
		start := time.Now()
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
			var angle_delta float64
			if angle == -1 {
				rad_angle = abs_angle(Point{x, y}.angle(checkpoints[nextCheckPointId].position))
				angle_delta = 0
			} else {
				rad_angle = float64(angle) * math.Pi / 180
				angle_delta = normalize_angle(rad_angle - pods[i].angle)
			}
			if pods[i].shield > 0 {
				pods[i].shield -= 1
				fmt.Fprintln(os.Stderr, "Shield active for pod: ", i)
			}
			pods[i].position = Point{x, y}
			pods[i].vx = vx
			pods[i].vy = vy
			pods[i].angle = rad_angle
			pods[i].angle_delta = angle_delta
			pods[i].nextCheckPointId = nextCheckPointId

			RANK[i].d2cp = pods[i].position.distance(checkpoints[nextCheckPointId].position) // the distance is squared
			if nextCheckPointId != RANK[i].checkPointId {
				RANK[i].checkPointId = nextCheckPointId
				if nextCheckPointId == 0 {
					RANK[i].lap += 1
				}
			}
		}

		// fmt.Fprintln(os.Stderr, "Debug messages...")
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
		for i, r := range RANK_SORT {
			if r.lap == laps {
				pods[r.id].lastCP = true
			}
			pods[r.id].rank = i + 1
			fmt.Fprintln(os.Stderr, r)
		}

		if TURN == 0 {
			fmt.Println(pods[0].default_action(checkpoints))
		} else {
			fmt.Println(pods[0].predict_action(checkpoints, pods))
		}
		// fmt.Println(pods[0].predict_action(checkpoints, pods))
		fmt.Println(pods[1].predict_action(checkpoints, pods))

		elapsed := time.Since(start)
		fmt.Fprintln(os.Stderr, "Elapsed time: ", elapsed.Seconds())
		TURN++
	}
}
