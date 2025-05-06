from dataclasses import dataclass
from typing import Literal

import fire
from beartype import beartype

from .cluster import Distributed, Local, Run


@dataclass
@beartype
class LargeScaleR:
    """
    e.g. largescaler run --type=lasso local --node-count=30
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
    fire.Fire(LargeScaleR)
