import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal, override

import ckdl


@dataclass
class Run:
    type: Literal["lm", "sandbox", "lasso"]


@dataclass
class Node(ABC):
    run: Run

    @abstractmethod
    def to_kdl(self) -> ckdl.Node:
        pass


@dataclass
class Master(Node):
    locator_port: int

    @override
    def __str__(self) -> str:
        return "LargeScaleR Master Node"

    def _run_cmd(self) -> list[str]:
        match self.run.type:
            case "lasso":
                run = "demo(lasso)"
            case "sandbox":
                run = ""
            case _:
                raise TypeError
        return [
            "--run=R",
            "library(largescaler)",
            f"# chunknet::LOCATOR({self.locator_port})",
            run,
            "1+1",
            "-",
            "interact",
        ]

    @override
    def to_kdl(self) -> ckdl.Node:
        return ckdl.Node(
            "pane",
            children=[
                ckdl.Node("focus", [True]),
                ckdl.Node("name", [str(self)]),
                ckdl.Node("command", ["run-interactive"]),
                ckdl.Node("args", self._run_cmd()),
            ],
        )


@dataclass
class Locator(Node):
    port: int

    @override
    def to_kdl(self) -> ckdl.Node: ...


@dataclass
class Worker(Node):
    port: int

    @override
    def to_kdl(self) -> ckdl.Node: ...


class Cluster(ABC):
    master: Master
    locator: Locator
    workers: list[Worker]
    run: Run

    @abstractmethod
    def exec(
        self,
    ):
        pass


@dataclass
class Local(Cluster):
    def __init__(self, run: Run, node_count: int):
        self.node_count: int = node_count
        self.run: Run = run

        locator_port = 8000
        next_port = locator_port + 1
        self.master: Master = Master(self.run, locator_port)
        self.locator: Locator = Locator(self.run, locator_port)
        self.compute_nodes: list[Worker] = [
            Worker(self.run, p)
            for p in range(next_port, next_port + self.node_count + 1)
        ]

    @override
    def exec(self):
        layout = self.to_kdl()
        self.__exec_layout(layout)

    def to_kdl(self) -> ckdl.Document:
        statusbar = ckdl.Node(
            "pane",
            properties={"size": 1, "borderless": True},
            children=[
                ckdl.Node("plugin", properties={"location": "zellij:compact-bar"})
            ],
        )
        return ckdl.Document(
            ckdl.Node(
                "layout",
                children=[
                    ckdl.Node(
                        "tab",
                        properties={"name": "Master"},
                        children=[self.master.to_kdl(), statusbar], # TODO Also include tab bar
                    ),
                    # ckdl.Node(name="tab", children=[self.locator.to_kdl()]),
                    # ckdl.Node(name="tab", children=[node.to_kdl() for node in self.compute_nodes]),
                ],
            )
        )

    def __exec_layout(self, layout: ckdl.Document):
        text = layout.dump(ckdl.EmitterOptions(version=1))
        with NamedTemporaryFile("w", suffix=".kdl", delete=False) as tmp:
            _ = tmp.write(text)
            tmp_path = Path(tmp.name)
        print(f"zellij --layout={tmp_path}")
        os.execvp("zellij", ["zellij", f"--layout={tmp_path}"])


@dataclass
class Distributed(Cluster):
    config_file: str

    @override
    def exec(self):
        pass
