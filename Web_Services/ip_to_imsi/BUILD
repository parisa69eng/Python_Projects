load("@io_bazel_rules_docker//docker/package_managers:download_pkgs.bzl", "download_pkgs")
load("@io_bazel_rules_docker//docker/package_managers:install_pkgs.bzl", "install_pkgs")
load("@io_bazel_rules_docker//container:container.bzl", "container_image", "container_push")
load("@io_bazel_rules_docker//docker/util:run.bzl", "container_run_and_commit")
load("@com_github_bazelbuild_buildtools//buildifier:def.bzl", "buildifier")
load("//web_services:version.bzl", "WEB_SERVICES_VERSION_FULL")

download_pkgs(
    name = "python3_pkgs",
    image_tar = "@ubuntu22.04//image",
    packages = [
        "python3",
        "python3-pip",
        "python3-setuptools",
        "vim",
    ],
)

install_pkgs(
    name = "python3_pkgs_image",
    image_tar = "@ubuntu22.04//image",
    installables_tar = ":python3_pkgs.tar",
    output_image_name = "python3_pkgs_image",
)

container_image(
    name = "ip_to_imsi_base_image",
    base = ":python3_pkgs_image.tar",
    files = [
        "main.py",
        "requirements.txt",
    ],
)

container_run_and_commit(
    name = "install_requirements",
    commands = [
        """python3 -m pip install -r requirements.txt""",
    ],
    image = ":ip_to_imsi_base_image.tar",
)

container_image(
    name = "ip_to_imsi",
    base = ":install_requirements",
    cmd = [
        "python3",
        "main.py",
    ],
    env = {
        "SETTINGS_PATH": "/etc/charging/ip_to_imsi/settings.json",
    },
    visibility = ["//visibility:public"],
    volumes = ["/etc/charging/ip_to_imsi/settings.json"],
)

container_push(
    name = "push_ip_to_imsi_docker_image",
    format = "Docker",
    image = ":ip_to_imsi",
    registry = "store.charging.inside.fdi.com:5243",
    repository = "charging/ip_to_imsi",
    tag = WEB_SERVICES_VERSION_FULL,
)

