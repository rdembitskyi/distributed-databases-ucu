from dataclasses import dataclass
import pathlib

import yaml


@dataclass
class ServerConfig:
    url: str


@dataclass
class LoadTestConfig:
    num_clients: int
    total_requests: int


@dataclass
class Config:
    server: ServerConfig
    load_test: LoadTestConfig

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        with pathlib.Path(yaml_path).open() as f:
            data = yaml.safe_load(f)

        return cls(
            server=ServerConfig(**data["server"]),
            load_test=LoadTestConfig(**data["load_test"]),
        )
