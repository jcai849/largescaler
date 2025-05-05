from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal, override
import textwrap

import ckdl
from beartype import beartype


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

    def _run_cmd(self) -> str:
        match self.run.type:
            case "lasso":
                run = "demo(lasso)"
            case "sandbox":
                run = ""
            case _:
                raise TypeError
        run_command = f"""\
        R
        # library(largescaler)
        # chunknet::LOCATOR({self.locator_port})
        # {run}
        1+1
        """
        return textwrap.dedent(run_command)

    @override
    def to_kdl(self) -> ckdl.Node:
        return ckdl.Node(
            "pane",
            children=[
                ckdl.Node("focus", [True]),
                ckdl.Node("name", [str(self)]),
                ckdl.Node("command", ["zellij"]),
                ckdl.Node("args", ["action", "write-chars", self._run_cmd()]),
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
        self.master: Master = Master(self.run, locator_port)
        self.locator: Locator = Locator(self.run, locator_port)
        self.compute_nodes: list[Worker] = [
            Worker(self.run, p) for p in range(locator_port + 1, self.node_count + 1)
        ]

    @override
    def exec(self):
        breakpoint()
        layout = self.to_kdl()
        self.__exec_layout(layout)

    def to_kdl(self) -> ckdl.Document:
        return ckdl.Document(
            ckdl.Node(
                "layout",
                children=[
                    ckdl.Node(
                        "tab",
                        properties={"name": "Master"},
                        children=[self.master.to_kdl()],
                    ),
                    # ckdl.Node(name="tab", children=[self.locator.to_kdl()]),
                    # ckdl.Node(name="tab", children=[node.to_kdl() for node in self.compute_nodes]),
                    ckdl.Node(
                        "pane",
                        properties={"size": 1, "borderless": True},
                        children=[
                            ckdl.Node(
                                "plugin", properties={"location": "zellij:compact-bar"}
                            )
                        ],
                    ),
                ],
            )
        )

    def __exec_layout(self, layout: ckdl.Document):
        text = layout.dump(ckdl.EmitterOptions(version=1))
        with NamedTemporaryFile('w', suffix='.kdl', delete=False) as tmp:
            _ = tmp.write(text)
            tmp_path = Path(tmp.name)
        os.execvp('zellij', ['--layout', str(tmp_path)])

@dataclass
class Distributed(Cluster):
    config_file: str

    @override
    def exec(self):
        pass


@dataclass
@beartype
class LargeScaleR:
    """
    e.g. largescaler run --type=lasso --n=300000000 --m=100 local --nodes=30
    """

    _run: Run | None = None
    _cluster: Local | Distributed | None = None

    ### Commands

    def run(self, type: Literal["sandbox", "lm", "lasso"]):
        self._run = Run(type=type)
        return self.__ready()

    def local(self, node_count: int):
        if not self._run:
            raise Exception
        self._cluster = Local(self._run, node_count)
        return self.__ready()

    def distributed(self, config_file: str):
        self._cluster = Distributed(config_file)
        return self.__ready()

    ### Runners

    def __ready(self):
        if self._run and self._cluster:
            self.__run()
        else:
            return self

    def __run(self):
        if self._run and self._cluster:
            self._cluster.exec()
        else:
            raise AttributeError


def main():
    import fire

    fire.Fire(LargeScaleR)


if __name__ == "__main__":
    main()
