from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'Send Messages to Telegram'
LONG_DESCRIPTION = 'Wrapper around the python-telegram-bot to use in threads'

setup(
    name="fbra-telegram",
    version=VERSION,
    author="Felix Brändli",
    author_email="",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=["python-telegram-bot[ext]"],

    keywords=['python', 'python-telegram-bot', 'wrapper'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)