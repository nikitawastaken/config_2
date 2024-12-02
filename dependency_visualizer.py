import gzip
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