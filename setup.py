from setuptools import setup, find_packages


# Safely read the version from twitchschedulerpy/__init__.py
def get_version():
    version = None
    with open("twitchschedulerpy/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"')
                break
    if version is None:
        raise RuntimeError(
            "Unable to find version string in twitchschedulerpy/__init__.py"
        )
    return version


# Safely read the long description from README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="twitch_scheduler_py",  # Package name
    version=get_version(),  # Use version from __init__.py
    packages=find_packages(include=["twitchschedulerpy", "twitchschedulerpy.*"]),
    install_requires=[
        "keyring==25.7.0",
        "setuptools==75.8.0",
        "platformdirs==4.9.4"
    ],
    extras_require={"dev": ["pipreqs", "black"]},
    entry_points={
        "console_scripts": [
            "twitchschedulerpy=twitchschedulerpy.main:main",  # entry-point for twitchschedulerpy
            "tws=twitchschedulerpy.main:main",  # entry-point shorthand
        ],
    },
    author="Gewerd Strauss",
    author_email="/",  # Replace with a valid email address
    description="A WIP port of https://github.com/Gewerd-Strauss/Twitch-Scheduler",
    long_description=long_description,  # Use the long description read from README.md
    long_description_content_type="text/markdown",
    url="https://github.com/Gewerd-Strauss/twitch_scheduler_py",  # Project URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.6",  # Minimum Python version requirement
)
