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
    @abstractmethod
    def to_kdl(self) -> ckdl.Node:
        pass


@dataclass
class Master(Node):
    run: Run
    locator_port: int

    def _run_cmd(self) -> list[str]:
        match self.run.type:
            case "lasso":
                run = 'demo("lasso", package="largescaler", ask=T, echo=T)'
            case "sandbox":
                run = ""
            case _:
                raise TypeError
        return [
            "--run=radian",
            "library(largescaler)",
            "orcv::start()",
            f'chunknet::LOCATOR("localhost", {self.locator_port})',
            run,
            "-",
            "interact",
        ]

    @override
    def to_kdl(self) -> ckdl.Node:
        return ckdl.Node(
            "pane",
            properties={"split_direction": "vertical"},
            children=[
                ckdl.Node(
                    "pane",
                    children=[
                        ckdl.Node("focus", [True]),
                        ckdl.Node("name", [str(self)]),
                        ckdl.Node("command", ["run-interactive"]),
                        ckdl.Node("args", self._run_cmd()),
                    ],
                ),
                ckdl.Node("pane", properties={"edit": "demo/lasso.R"}),
            ],
        )


@dataclass
class Locator(Node):
    port: int

    def _run_cmd(self):
        return [
            "-e",
            "library(largescaler);"
            + f'chunknet::locator_node("localhost", {self.port}L, verbose=TRUE)',
        ]

    @override
    def to_kdl(self) -> ckdl.Node:
        return ckdl.Node(
            "pane",
            children=[
                ckdl.Node("focus", [True]),
                ckdl.Node("name", [str(self)]),
                ckdl.Node("command", ["Rscript"]),
                ckdl.Node("args", self._run_cmd()),
            ],
        )


@dataclass
class Worker(Node):
    port: int
    locator_port: int

    def _run_cmd(self):
        return [
            "-e",
            "library(largescaler);"
            + "Sys.sleep(2);"
            + f'chunknet::worker_node("localhost", {self.port}L,'
            + 'locator_address="localhost",'
            + f"locator_port={self.locator_port}L, verbose=T)",
        ]

    @override
    def to_kdl(self) -> ckdl.Node:
        return ckdl.Node(
            "pane",
            children=[
                ckdl.Node("focus", [True]),
                ckdl.Node("name", [str(self)]),
                ckdl.Node("command", ["Rscript"]),
                ckdl.Node("args", self._run_cmd()),
            ],
        )


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

        locator_port = 9000
        next_port = locator_port + 1
        self.master: Master = Master(self.run, locator_port)
        self.locator: Locator = Locator(locator_port)
        self.workers: list[Worker] = [
            Worker(p, locator_port)
            for p in range(next_port, next_port + self.node_count + 1)
        ]

    @override
    def exec(self):
        layout = self.to_kdl()
        self.__exec_layout(layout)

    def to_kdl(self) -> ckdl.Document:
        status_bar = ckdl.Node(
            "pane",
            properties={"size": 1, "borderless": True},
            children=[
                ckdl.Node("plugin", properties={"location": "zellij:status-bar"})
            ],
        )
        tab_bar = ckdl.Node(
            "pane",
            properties={"size": 1, "borderless": True},
            children=[ckdl.Node("plugin", properties={"location": "zellij:tab-bar"})],
        )
        return ckdl.Document(
            ckdl.Node(
                "layout",
                children=[
                    ckdl.Node(
                        "tab",
                        properties={"name": "Master"},
                        children=[tab_bar, self.master.to_kdl(), status_bar],
                    ),
                    ckdl.Node(
                        "tab",
                        properties={"name": "Locator"},
                        children=[tab_bar, self.locator.to_kdl(), status_bar],
                    ),
                    ckdl.Node(
                        "tab",
                        properties={"name": "Workers"},
                        children=[
                            tab_bar,
                            ckdl.Node(
                                "pane",
                                properties={"stacked": True},
                                children=[w.to_kdl() for w in self.workers],
                            ),
                            status_bar,
                        ],
                    ),
                ],
            ),
            ckdl.Node("show_startup_tips", args=[False]),
            ckdl.Node("show_release_notes", args=[False]),
            ckdl.Node(
                "ui",
                children=[
                    ckdl.Node(
                        "pane_frames",
                        children=[
                            ckdl.Node("rounded_corners", args=[True]),
                            ckdl.Node("hide_session_name", args=[True]),
                        ],
                    )
                ],
            ),
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
