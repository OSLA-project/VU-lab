# Pull the ROS2 distro.
# This will set the ROS_DISTRO env variable (in this case, 'jazzy').
FROM osrf/ros:jazzy-desktop-noble

# Reconfigure the shell to use bash
# so that we can use `source`
RUN unlink /bin/sh && ln -s /bin/bash /bin/sh

# Set up the user
ENV OLD_USER="ubuntu"
ARG USER=${OLD_USER}
ENV HOME=/home/${USER}
ENV WORKSPACE_DIR=${HOME}/dev_ws/src
ENV CONTROLLER_DIR=${HOME}/controller
ENV XARM_ROS_REPO="https://github.com/xArm-Developer/xarm_ros2.git"
ENV DISPLAY=:0

# Update the repos and install ROS2 packages.
RUN apt update && apt install \
    --yes ros-${ROS_DISTRO}-moveit \
    ros-${ROS_DISTRO}-ament-cmake-vendor-package \
    ros-${ROS_DISTRO}-ament-cmake \
    micro apt-utils

# Set up the user so that we can mount volumes without permission problems
RUN usermod -l ${USER} ${OLD_USER} && usermod -d ${HOME} -m ${USER} && groupmod -n ${USER} ${OLD_USER}

# Allow sudo without a password
RUN echo ${USER} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER} && chmod 0440 /etc/sudoers.d/${USER}

# Set up the working environment
# - Drop to user
# - Set up directories
USER ${USER}:${USER}
WORKDIR ${WORKSPACE_DIR}
RUN mkdir -p ${WORKSPACE_DIR}

# Set up the xArm codebase.
# This follows the instructions from https://github.com/xArm-Developer/xarm_ros2.
# First, clone the xArm repo and update it.
RUN git clone ${XARM_ROS_REPO} --recursive -b ${ROS_DISTRO}

WORKDIR ${WORKSPACE_DIR}/xarm_ros2
RUN git pull --recurse-submodules
WORKDIR ${WORKSPACE_DIR}

# Update ROS dependencies
RUN rosdep update && rosdep install --from-paths . --ignore-src --rosdistro ${ROS_DISTRO} -y

# Build all packages
WORKDIR ${HOME}/dev_ws
RUN source "/opt/ros/${ROS_DISTRO}/setup.bash" && colcon build

# Mount host directories
VOLUME [${CONTROLLER_DIR}]

# Add some convenience commands to ~/.bashrc
# so we don't have to run them manually every time.
RUN echo -e "source ~/dev_ws/install/setup.bash\nexport COLORTERM=truecolor\nexport MICRO_TRUECOLOR=1" >> ${HOME}/.bashrc
