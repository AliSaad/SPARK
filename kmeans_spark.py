#  Find K Means of Loudacre device status locations
#
# Input data: file(s) with device status data (delimited by '|')
# including latitude (13th field) and longitude (14th field) of device locations
# (lat,lon of 0,0 indicates unknown location)
#
# NOTE: Copy to pyspark using %paste
from pyspark import SparkContext


# for a point p and an array of points, return the index in the array of the point closest to p
def closestPoint(p, points):
    bestIndex = 0
    closest = float("+inf")
    # for each point in the array, calculate the distance to the test point, then return
    # the index of the array point with the smallest distance
    for i in range(len(points)):
        dist = distanceSquared(p, points[i])
        if dist < closest:
            closest = dist
            bestIndex = i
    return bestIndex


# The squared distances between two points
def distanceSquared(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


# The sum of two points
def addPoints(p1, p2):
    return [p1[0] + p2[0], p1[1] + p2[1]]


# The files with device status data
filename = "/loudacre/devicestatus_etl/*"

# K is the number of means (center points of clusters) to find
K = 5

# ConvergeDist -- the threshold "distance" between iterations at which we decide we are done
convergeDist = 1

# Parse device status records into [latitude,longitude]
# Filter out records where lat/long is unavailable -- ie: 0/0 points
# TODO
sc = SparkContext()
points = sc.textFile(filename) \
    .map(lambda line: line.split(",")) \
    .map(lambda fields: [float(fields[3]), float(fields[4])]) \
    .filter(lambda point: sum(point) != 0) \
    .persist()

# start with K randomly selected points from the dataset
# TODO
kPoints = points.takeSample(False, K, 18)
print "StartPoint", kPoints

# loop until the total distance between one iteration's points and the next is less than the convergence distance specified
tempDist = float("+inf")
while tempDist > convergeDist:
    # for each point, find the index of the closest kpoint.  map to (index, (point,1))
    # TODO
    closest = points.map(lambda p: (closestPoint(p, kPoints), (p, 1)))
    # For each key (k-point index), reduce by adding the coordinates and number of points
    # TODO
    pointStats = closest.reduceByKey(lambda (point1, n1), (point2, n2):
                                     (addPoints(point1, point2), n1 + n2))
    # For each key (k-point index), find a new point by calculating the average of each closest point
    # TODO
    newPoints = pointStats.map(lambda (i, (point, n)):
                               (i, [point[0] / n, point[1] / n])).take(50)
    # calculate the total of the distance between the current points and new points
    # TODO
    iDist = 0
    for (i, point) in newPoints: iDist += distanceSquared(kPoints[i], point)
    print "DistBetweenPoints", iDist
    # Copy the new points to the kPoints array for the next iteration
    # TODO
    for (i, point) in newPoints: kPoints[i] = point

    # Display the final points
    # TODO
print "Kmeans" + str(kPoints)