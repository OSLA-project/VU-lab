# Pull the ROS2 distro.
# This will set the ROS_DISTRO env variable (in this case, 'jazzy').
FROM osrf/ros:jazzy-desktop-noble

# Reconfigure the shell to use bash
# so that we can use `source`.
RUN unlink /bin/sh && ln -s /bin/bash /bin/sh

# Set up the user and some useful directories
ENV USER="ubuntu"
ENV HOME=/home/${USER}
ENV WORKSPACE_DIR=${HOME}/dev_ws
ENV SRC_DIR=${WORKSPACE_DIR}/src

# Allow sudo without a password
RUN echo ${USER} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER} && chmod 0440 /etc/sudoers.d/${USER}

# Update the repos and install ROS2 packages.
RUN apt update && apt install ros-${ROS_DISTRO}-rclpy

# Drop to user
USER ${USER}:${USER}

# Mount host directories and adjust permissions.
COPY ./dev_ws/src ${SRC_DIR}
RUN sudo chown -R ${USER}:${USER} ${WORKSPACE_DIR}
VOLUME ${SRC_DIR}
WORKDIR ${WORKSPACE_DIR}

# Update ROS dependencies
RUN rosdep update && rosdep install --from-paths . --ignore-src --rosdistro ${ROS_DISTRO} -y

# Build all packages
RUN source "/opt/ros/${ROS_DISTRO}/setup.bash" && colcon build

# Add some convenience commands to ~/.bashrc
# so we don't have to run them manually every time.
RUN echo -e "source /opt/ros/${ROS_DISTRO}/setup.bash\nsource ~/dev_ws/install/setup.bash" >> ${HOME}/.bashrc
