import random
import numpy as np

def generate_random_points(num_points, range):
    return (np.random.randint(-range, range, num_points),
            np.random.randint(-range, range, num_points),
            np.random.randint(-range, range, num_points))