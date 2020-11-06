from test.base import ArtemisModuleTestCase
from typing import NamedTuple

from karton.core import Task

from artemis.binds import TaskType
from artemis.modules.classifier import Classifier


class TestData(NamedTuple):
    raw: str
    expected: str
    type: TaskType


class ClassifierTest(ArtemisModuleTestCase):
    karton_class = Classifier

    def test_parsing(self) -> None:
        urls = [
            TestData("https://cert.pl", "cert.pl", TaskType.DOMAIN),
            TestData("http://cert.pl", "cert.pl", TaskType.DOMAIN),
            TestData("hxxps://cert.pl", "cert.pl", TaskType.DOMAIN),
            TestData("hxxp://cert.pl", "cert.pl", TaskType.DOMAIN),
            TestData("https://cert[.]pl", "cert.pl", TaskType.DOMAIN),
            TestData("cert.pl", "cert.pl", TaskType.DOMAIN),
            TestData("cert.pl:8080", "cert.pl", TaskType.DOMAIN),
            TestData("ws://cert.pl", "cert.pl", TaskType.DOMAIN),
            TestData("root@cert.pl", "cert.pl", TaskType.DOMAIN),
            TestData("ssh://cert.pl", "cert.pl", TaskType.DOMAIN),
            TestData("ssh://127.0.0.1", "127.0.0.1", TaskType.IP),
            TestData("127.0.0.1:8080", "127.0.0.1", TaskType.IP),
        ]

        for entry in urls:
            self.karton.cache.flush()
            task = Task({"type": TaskType.NEW}, payload={"data": entry.raw})
            results = self.run_task(task)

            expected_task = Task(
                {"type": entry.type, "origin": self.karton_class.identity},
                payload={entry.type: entry.expected},
            )

            self.assertTasksEqual(results, [expected_task])

    def test_invalid_url(self) -> None:
        task = Task({"type": TaskType.NEW}, payload={"data": "INVALID_DATA"})

        with self.assertRaises(ValueError):
            results = self.run_task(task)
            self.assertListEqual(results, [])
