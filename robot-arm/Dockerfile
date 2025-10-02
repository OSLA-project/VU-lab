# Pull the ROS2 distro.
# This will set the ROS_DISTRO env variable (in this case, 'jazzy').
FROM osrf/ros:jazzy-desktop
CMD echo "==[ ROS distro: ${ROS_DISTRO}"

# Reconfigure the shell to use bash
# so that we can use `source`
RUN unlink /bin/sh && ln -s /bin/bash /bin/sh

# Set the user name.
ARG USER="ubuntu"
ARG USER_UID=1000
ARG USER_GID=${USER_UID}
ARG HOME=/home/${USER}
ARG WORKSPACE_DIR=${HOME}/dev_ws/src
ARG XARM_ROS_REPO="https://github.com/xArm-Developer/xarm_ros2.git"

# Update the repos and install.
RUN apt update
RUN apt install --yes ros-${ROS_DISTRO}-moveit ros-${ROS_DISTRO}-ros-gz \
    ros-${ROS_DISTRO}-ament-cmake-vendor-package ros-${ROS_DISTRO}-ament-cmake

# Set up the working environment
# - Drop to user
# - Set up directories
USER ${USER}:${USER}
RUN mkdir -p ${WORKSPACE_DIR}

RUN echo "==[ Running as user" `whoami`
# RUN source "/opt/ros/${ROS_DISTRO}/setup.bash"
WORKDIR ${WORKSPACE_DIR}

# Set up the xArm codebase.
# This follows the instructions from https://github.com/xArm-Developer/xarm_ros2.
# First, clone the xArm repo and update it.
RUN git clone ${XARM_ROS_REPO} --recursive -b ${ROS_DISTRO}

WORKDIR ${WORKSPACE_DIR}/xarm_ros2
RUN git pull --recurse-submodules
WORKDIR ${WORKSPACE_DIR}

# Update ROS dependencies
RUN rosdep update

USER root:root
RUN rosdep install --from-paths . --ignore-src --rosdistro ${ROS_DISTRO} -y

USER ${USER}:${USER}
WORKDIR ${HOME}/dev_ws

# Build all packages
RUN source "/opt/ros/${ROS_DISTRO}/setup.bash" && colcon build
