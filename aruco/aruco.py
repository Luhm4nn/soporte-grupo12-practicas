import cv2
import cv2.aruco as aruco
import numpy as np
import time
import math

camera_matrix = np.array([
    [800, 0, 320],
    [0, 800, 240],
    [0, 0, 1]
], dtype=np.float32)

dist_coeffs = np.zeros((5, 1), dtype=np.float32)

marker_length = 0.05
half_l = marker_length / 2

marker_points = np.array([
    [-half_l,  half_l, 0],
    [ half_l,  half_l, 0],
    [ half_l, -half_l, 0],
    [-half_l, -half_l, 0]
], dtype=np.float32)

dictionary = aruco.getPredefinedDictionary(
    aruco.DICT_6X6_250
)

parameters = aruco.DetectorParameters()

detector = aruco.ArucoDetector(
    dictionary,
    parameters
)


planets = [
    ("Mercurio", 0.02, 2.0, 4),
    ("Venus",    0.03, 1.5, 5),
    ("Tierra",   0.04, 1.0, 6),
    ("Marte",    0.05, 0.8, 5)
]

start_time = time.time()

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:

        for marker in corners:

            success, rvec, tvec = cv2.solvePnP(
                marker_points,
                marker[0],
                camera_matrix,
                dist_coeffs
            )

            if not success:
                continue

            t = time.time() - start_time

            sun_3d = np.array([
                [0, 0, 0]
            ], dtype=np.float32)

            sun_2d, _ = cv2.projectPoints(
                sun_3d,
                rvec,
                tvec,
                camera_matrix,
                dist_coeffs
            )

            sun_pt = tuple(
                np.int32(sun_2d[0][0])
            )

            cv2.circle(
                frame,
                sun_pt,
                12,
                (0, 255, 255),
                -1
            )
            for i, (_, radius, speed, size) in enumerate(planets):

                angle = t * speed

                x = radius * math.cos(angle)
                y = radius * math.sin(angle)

                planet_3d = np.array([
                    [x, y, 0]
                ], dtype=np.float32)

                orbit_points = []

                for deg in range(0, 360, 10):

                    a = math.radians(deg)

                    orbit_points.append([
                        radius * math.cos(a),
                        radius * math.sin(a),
                        0
                    ])

                orbit_points = np.array(
                    orbit_points,
                    dtype=np.float32
                )

                orbit_2d, _ = cv2.projectPoints(
                    orbit_points,
                    rvec,
                    tvec,
                    camera_matrix,
                    dist_coeffs
                )

                orbit_2d = np.int32(
                    orbit_2d.reshape(-1, 2)
                )

                cv2.polylines(
                    frame,
                    [orbit_2d],
                    True,
                    (200, 200, 200),
                    1
                )

                planet_2d, _ = cv2.projectPoints(
                    planet_3d,
                    rvec,
                    tvec,
                    camera_matrix,
                    dist_coeffs
                )

                px, py = np.int32(
                    planet_2d[0][0]
                )

                color = [
                    (120,120,120),
                    (0,180,255),
                    (255,0,0),
                    (0,0,255)
                ][i]

                cv2.circle(
                    frame,
                    (px, py),
                    size,
                    color,
                    -1
                )

            cv2.drawFrameAxes(
                frame,
                camera_matrix,
                dist_coeffs,
                rvec,
                tvec,
                0.03
            )

    cv2.imshow(
        "Sistema Solar AR",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()