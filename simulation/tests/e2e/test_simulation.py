from utils import simulate
import os

def test_simualtion():
    os.mkdir("log")
    simulate.simulate(
            "pytest",
            "us-east-1",
            "ap-southeast-2",
            "t2.micro",
            "t2.micro",
            "ami-053b0d53c279acc90",
            "ami-0310483fb2b488153",
            100, 100, 100, 100,
            "test_src_clean",
            60,
            "s3://raw-src-files/recordings/"
            )