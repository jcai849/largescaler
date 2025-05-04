from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, override

import ckdl
from beartype import beartype


@dataclass
class Demo:
    type: Literal["lm", "sandbox", "lasso"]


class Node(ABC):
    @abstractmethod
    def to_kdl(self, what: Demo) -> ckdl.Node:
        pass


@dataclass
class Master(Node):
    port: int
    locator_port: int

    @override
    def to_kdl(self, what: Demo) -> ckdl.Node:
        ...


@dataclass
class Locator(Node):
    port: int

    @override
    def to_kdl(self, what: Demo) -> ckdl.Node:
        ...


@dataclass
class Worker(Node):
    port: int

    @override
    def to_kdl(self, what: Demo) -> ckdl.Node:
        ...


class Topology(ABC):
    @abstractmethod
    def run(self, what: Demo):
        pass


@dataclass
class Local(Topology):
    node_count: int

    @override
    def run(self, what: Demo):
        layout = self.make_layout(what)
        self.exec_layout(layout)

    def make_layout(self, what: Demo) -> ckdl.Document:  
        locator_port = 8001
        master_port = locator_port - 1
        master = Master(master_port, locator_port)
        locator = Locator(locator_port)
        compute_nodes = [
            Worker(p) for p in range(locator_port + 1, self.node_count + 1)
        ]

        return ckdl.Document(  
            ckdl.Node("tab", master.to_kdl(what)),  
            ckdl.Node("tab", locator.to_kdl(what)),  
            ckdl.Node("tab", children=[node.to_kdl(what) for node in compute_nodes]),  
        )

    def exec_layout(self, layout: ckdl.Document):  
        ...
        # dump and write file to tmp
        # exec zellij with file


@dataclass
class Distributed(Topology):
    config_file: str

    @override
    def run(self, what: Demo):
        pass


@dataclass
@beartype
class LargeScaleR:
    """
    e.g. largescaler demo --type=lasso --n=300000000 --m=100 local --nodes=30
    """

    _demo: Demo | None = None
    _topology: Local | Distributed | None = None

    ### Commands

    def demo(self, type: Literal["sandbox", "lm", "lasso"]):
        self._demo = Demo(type=type)
        return self.__ready()

    def local(self, node_count: int):
        self._topology = Local(node_count)
        return self.__ready()

    def distributed(self, config_file: str):
        self._topology = Distributed(config_file)
        return self.__ready()

    ### Runners

    def __ready(self):
        if self._demo and self._topology:
            self.__run()
        else:
            return self

    def __run(self):
        if self._demo and self._topology:
            self._topology.run(self._demo)
        else:
            raise AttributeError


def main():
    import fire

    fire.Fire(LargeScaleR)


if __name__ == "__main__":
    main()
