import textwrap
import docker

client = docker.from_env()

CONTAINER_NAME = "geogridfusion-pg"

POSTGRES_PASSWORD = "password"
POSTGRES_USER = "postgres"
POSTGRES_DB = "postgres"


def run_container(
    image="postgis/postgis:14-3.5",
    accept_docker: bool | None = None,
    dry_run: bool = False,
    host_port: int = 5433,
    data_dir: str | None = None,
):
    """
    Pulls IMAGE from Docker Hub and runs it locally. This will download
    an image (hundreds of MB) and start a container on your machine.

    To proceed, pass accept_docker=True.
    """

    banner = textwrap.dedent(f"""
    === GeoGridFusion will use Docker ===
    - Action: PULL & RUN a container image
    - Image:  {image}
    - Source: Docker Hub
    - Port:   127.0.0.1:{host_port} -> container:5432
    - Data:   {'named volume "pgdata"' if not data_dir else data_dir + " -> /var/lib/postgresql/data"}

    This will download data from the internet and start a background service.
    """).strip()
    print(banner)

    if dry_run:
        print("[dry-run] No changes made.")
        return

    if not accept_docker:
        raise RuntimeError(
            "Refusing to pull/run a Docker image without explicit consent.\n"
            "Re-run with accept_docker=True."
        )

    try:
        c = client.containers.get(CONTAINER_NAME)
        c.reload()

        if c.status == "running":
            print(f"{CONTAINER_NAME} already running (id={c.short_id})")
            return c
        else:
            print(f"{CONTAINER_NAME} exists with status '{c.status}', starting…")
            c.start()
            c.reload()
            print(f"{CONTAINER_NAME} status: {c.status}")
            return c

    except docker.errors.NotFound:  # type: ignore
        print(f"{CONTAINER_NAME} not found; creating…")
        c = client.containers.run(
            image=image,
            name=CONTAINER_NAME,
            detach=True,
            environment={
                "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
                "POSTGRES_UESR": POSTGRES_USER,
                "POSTGRES_DB": POSTGRES_DB,
            },
            ports={"5432/tcp": 5432},
            volumes={"pgdata": {"bind": "/var/lib/postgresql/data", "mode": "rw"}},
            restart_policy={"Name": "unless-stopped"},  # type: ignore
        )  # type: ignore

        print(f"Created {CONTAINER_NAME} (id={c.short_id})")
        return c
    except docker.errors.APIError as e:  # type: ignore
        raise RuntimeError(f"Docker API error: {e.explanation}") from e
