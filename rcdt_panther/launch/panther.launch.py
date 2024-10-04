# SPDX-FileCopyrightText: Alliander N. V.
#
# SPDX-License-Identifier: Apache-2.0

from launch import LaunchDescription, LaunchContext, LaunchDescriptionEntity
from launch.actions import OpaqueFunction, IncludeLaunchDescription
from launch_ros.actions import Node, SetParameter

from rcdt_utilities.launch_utils import (
    get_file_path,
    get_robot_description,
    LaunchArgument,
)

run_rviz_arg = LaunchArgument("rviz", False, [True, False])


def launch_setup(context: LaunchContext) -> None:
    xacro_path = get_file_path("panther_description", ["urdf"], "panther.urdf.xacro")
    xacro_arguments = {"use_sim": "true"}
    robot_description = get_robot_description(xacro_path, xacro_arguments)

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
    )

    robot = IncludeLaunchDescription(
        get_file_path("rcdt_utilities", ["launch"], "gazebo_robot.launch.py")
    )

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    controllers = IncludeLaunchDescription(
        get_file_path("rcdt_panther", ["launch"], "controllers.launch.py"),
    )

    rviz = IncludeLaunchDescription(
        get_file_path("rcdt_utilities", ["launch"], "rviz.launch.py"),
        launch_arguments={"rviz_frame": "odom"}.items(),
    )

    gamepad = Node(
        package="rcdt_utilities",
        executable="gamepad_node.py",
    )

    skip = LaunchDescriptionEntity()
    return [
        SetParameter(name="use_sim_time", value=True),
        robot_state_publisher,
        robot,
        joint_state_broadcaster,
        controllers,
        rviz if run_rviz_arg.value(context) else skip,
        gamepad,
    ]


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            run_rviz_arg.declaration,
            OpaqueFunction(function=launch_setup),
        ]
    )
