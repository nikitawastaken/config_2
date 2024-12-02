import os
import gzip
import argparse
from graphviz import Digraph


def parse_packages_file(packages_file_path):
    """
    Парсит файл Packages и возвращает словарь зависимостей.
    """
    dependencies = {}
    current_package = None

    with gzip.open(packages_file_path, 'rt') if packages_file_path.endswith('.gz') else open(packages_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Package:"):
                current_package = line.split(":", 1)[1].strip()
                dependencies[current_package] = []
            elif line.startswith("Depends:") and current_package:
                deps = line.split(":", 1)[1].strip()
                dep_list = [dep.split()[0] for dep in deps.split(",")]
                dependencies[current_package].extend(dep_list)

    return dependencies


def build_dependency_graph(package_name, dependencies, graph=None, seen=None):
    """
    Рекурсивно строит граф зависимостей для пакета.
    """
    if graph is None:
        graph = {}
    if seen is None:
        seen = set()

    if package_name in seen or package_name not in dependencies:
        return graph

    seen.add(package_name)
    graph[package_name] = dependencies.get(package_name, [])

    for dep in graph[package_name]:
        build_dependency_graph(dep, dependencies, graph, seen)

    return graph


def visualize_dependency_graph(graph, output_path, graphviz_program):
    """
    Визуализирует граф зависимостей с помощью Graphviz.
    """
    dot = Digraph(format="png", engine=graphviz_program)
    
    for package, deps in graph.items():
        dot.node(package)
        for dep in deps:
            dot.edge(package, dep)
    
    dot.render(output_path, cleanup=True)


def main():
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов Ubuntu без сторонних утилит."
    )
    parser.add_argument("package", help="Имя анализируемого пакета")
    parser.add_argument(
        "--packages-file",
        required=True,
        help="Путь к файлу Packages или Packages.gz"
    )
    parser.add_argument(
        "--program",
        default="dot",
        help="Программа для визуализации графов (по умолчанию dot)"
    )
    parser.add_argument(
        "--output",
        default="dependencies",
        help="Путь для сохранения результата"
    )
    args = parser.parse_args()

    if not os.path.exists(args.packages_file):
        print(f"Файл {args.packages_file} не найден.")
        return

    try:
        dependencies = parse_packages_file(args.packages_file)
        graph = build_dependency_graph(args.package, dependencies)
        visualize_dependency_graph(graph, args.output, args.program)
        print(f"Граф зависимостей пакета {args.package} успешно сохранен в {args.output}.png.")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()