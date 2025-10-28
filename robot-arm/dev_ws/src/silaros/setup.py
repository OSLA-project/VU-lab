from setuptools import find_packages, setup

package_name = 'silaros'

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Alexander Hadjiivanov",
    maintainer_email="a.hadjiivanov@esciencecenter.nl",
    description="SiLA ROS2 connector for Ufactory / xArm robotic arms.",
    license="Apache-2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "sender = silaros.controller:main",
            "receiver = silaros.subscriber:main",
        ],
    },
)
