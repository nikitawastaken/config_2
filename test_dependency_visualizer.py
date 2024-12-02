import unittest
from unittest.mock import patch, mock_open
from dependency_visualizer import parse_packages_file, build_dependency_graph, visualize_dependency_graph


class TestDependencyVisualizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Тестовые данные файла Packages
        cls.packages_file_content = """
Package: package-a
Depends: package-b, package-c

Package: package-b
Depends: package-d

Package: package-c
Depends:

Package: package-d
Depends: package-e

Package: package-e
Depends:
"""

    def setUp(self):
        # Ожидаемые зависимости после парсинга
        self.expected_dependencies = {
            "package-a": ["package-b", "package-c"],
            "package-b": ["package-d"],
            "package-c": [],
            "package-d": ["package-e"],
            "package-e": []
        }

    @patch("gzip.open")
    def test_parse_packages_file_gz(self, mock_gzip_open):
        """
        Тест парсинга сжатого файла Packages.gz.
        """
        mock_gzip_open.return_value.__enter__.return_value = self.packages_file_content.splitlines(keepends=True)
        dependencies = parse_packages_file("Packages.gz")
        self.assertEqual(dependencies, self.expected_dependencies)

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_parse_packages_file_plain(self, mock_open_file):
        """
        Тест парсинга обычного файла Packages.
        """
        mock_open_file.return_value.__enter__.return_value = self.packages_file_content.splitlines(keepends=True)
        dependencies = parse_packages_file("Packages")
        self.assertEqual(dependencies, self.expected_dependencies)

    def test_build_dependency_graph(self):
        """
        Тест построения графа зависимостей.
        """
        graph = build_dependency_graph("package-a", self.expected_dependencies)
        expected_graph = {
            "package-a": ["package-b", "package-c"],
            "package-b": ["package-d"],
            "package-c": [],
            "package-d": ["package-e"],
            "package-e": []
        }
        self.assertEqual(graph, expected_graph)

    @patch("dependency_visualizer.Digraph")
    def test_visualize_dependency_graph(self, mock_digraph):
        """
        Тест визуализации графа зависимостей.
        """
        graph = {
            "package-a": ["package-b", "package-c"],
            "package-b": ["package-d"],
            "package-c": [],
            "package-d": ["package-e"],
            "package-e": []
        }
        mock_dot = mock_digraph.return_value

        # Вызываем функцию визуализации
        visualize_dependency_graph(graph, "test_output", "dot")

        # Проверяем, что узлы и связи добавлены
        mock_dot.node.assert_any_call("package-a")
        mock_dot.edge.assert_any_call("package-a", "package-b")
        mock_dot.edge.assert_any_call("package-a", "package-c")
        mock_dot.edge.assert_any_call("package-b", "package-d")
        mock_dot.edge.assert_any_call("package-d", "package-e")

        # Проверяем, что рендеринг был вызван
        mock_dot.render.assert_called_with("test_output", cleanup=True)

    def tearDown(self):
        """
        Очистка данных после тестов.
        """
        import os
        if os.path.exists("test_output.png"):
            os.remove("test_output.png")


if __name__ == "__main__":
    # Создаем тестовый набор
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDependencyVisualizer)
    
    # Запускаем тесты с более подробным выводом
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Выводим сообщение об успехе или ошибках
    if result.wasSuccessful():
        print("\nВсе тесты пройдены успешно! 🎉")
    else:
        print(f"\nТесты завершены с ошибками. Провалено: {len(result.failures)} тест(ов).")