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
# RUN apt update
# RUN apt install ros-${ROS_DISTRO}-moveit ros-${ROS_DISTRO}-ros-gz \
#     ros-${ROS_DISTRO}-ament-cmake-vendor-package ros-${ROS_DISTRO}-ament-cmake --yes

# Allow sudo without a password
RUN echo ${USER} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER}
RUN chmod 0440 /etc/sudoers.d/${USER}

# Set up the working environment
# - Drop to user
# - Set up directories
USER ${USER}:${USER}
RUN mkdir -p ${WORKSPACE_DIR}

RUN echo "==[ Running as user" `whoami`
RUN source "/opt/ros/${ROS_DISTRO}/setup.bash"
WORKDIR ${WORKSPACE_DIR}
RUN echo "==[ Current directory" `pwd`

# Set up the xArm codebase.
# This follows the instructions from https://github.com/xArm-Developer/xarm_ros2.
# First, clone the xArm repo and update it.
RUN git clone ${XARM_ROS_REPO} --recursive -b ${ROS_DISTRO}

WORKDIR ${WORKSPACE_DIR}/xarm_ros2
RUN git pull --recurse-submodules
WORKDIR ${WORKSPACE_DIR}

# Update ROS dependencies
USER root:root
RUN rosdep update
RUN rosdep install --from-paths . --ignore-src --rosdistro ${ROS_DISTRO} -y

USER ${USER}:${USER}
WORKDIR ${HOME}/dev_ws

# Build all packages
RUN colcon build
