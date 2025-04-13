"""
Скрипт установки пакета video_pipeline
"""
from setuptools import setup, find_packages

# Чтение описания из файла README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Чтение требований из файла requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="video_pipeline",
    version="0.1.0",
    author="Video Pipeline Team",
    author_email="example@example.com",
    description="Модульный конвейер обработки видео на Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/video_pipeline",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "video-pipeline=video_pipeline.cli:main",
        ],
    },
) 