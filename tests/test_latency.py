import requests
import time
import pytest
from bot.setting.config import config

DIFFICULTY = "medium"
TOPIC = "math"
NUM_TESTS = 10


def measure_latency(server_address, difficulty, topic, num_tests=10):
    latencies = []

    for _ in range(num_tests):
        start_time = time.time()
        response = requests.post(f"{server_address}/questions/",
                                 json={"difficulty": difficulty, "subject": topic}).json()
        end_time = time.time()

        latency = end_time - start_time
        latencies.append(latency)

    average_latency = sum(latencies) / num_tests
    return latencies, average_latency


def test_latency():
    latencies, average_latency = measure_latency(config.SERVER_URL, DIFFICULTY, TOPIC, NUM_TESTS)

    assert len(latencies) == NUM_TESTS, f"Expected {NUM_TESTS} latency measurements, but got {len(latencies)}."

    for i, latency in enumerate(latencies):
        diff_from_average = latency - average_latency
        print(f"Test {i + 1}: {latency:.4f} seconds (Difference from average: {diff_from_average:.4f} seconds)")
        assert abs(diff_from_average) < 2, f"Latency test {i + 1} is more than 2 second away from the average latency."
