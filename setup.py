from setuptools import setup, find_packages

def get_requirments(filename):
    reqs = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(("#", "--")):
                continue
            if "://" in line or line.startswith(".") or line.startswith("git+"):
                continue
            reqs.append(line)
    print(f"Requirements loaded: {reqs}")
    return reqs


setup(
    name="whisper_proj",
    author = "sarfraz",
    version= "0.0.1",
    description="A project for testing Whisper",
    packages=find_packages(),
    install_requires=get_requirments('requirments.txt'),
)