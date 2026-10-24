import sys
import logging
import networkx as nx

from WeightType import WeightType


class Graph:

    @staticmethod
    def create_dependencies(classes, graph):
        """ Based on the data parsed from the AST by the javaparser adds and weighted edge.
            Edges are added to references between 2 classes for every:
                - reference of variable, field, etc.
                - method call invocation in a given class
        """
        for classe in classes.values():

            # Add implement relationships
            Graph.add_edges_dependencies(
                classe, classes, classe.get_implemented_types(), graph, 'IMPLEMENTS')

            # Add inheritance relatonships
            Graph.add_edges_dependencies(
                classe, classes, classe.get_extended_types(), graph, 'EXTENDS')

            # Add edges for references created by variables and method parameters and return types
            Graph.add_edges_dependencies(
                classe, classes, classe.get_dependencies(), graph, 'NORMAL')

            # Add edges for method call invocations to other classes
            Graph.add_edges_dependencies(
                classe, classes, [m['targetClassName'] for m in classe.get_method_invocations()], graph, 'METHOD_CALL')

        return graph

    @staticmethod
    def to_undirected(graph):
        """ Take into consideration the weighted edges and select the max.
        nx.to_undirected() keeps the last weight """
        G = nx.Graph()
        new_edges = {}
        for src, dst in graph.copy().edges():
            if (src, dst) in new_edges or (dst, src) in new_edges:
                continue

            edge_data_1 = graph.get_edge_data(src, dst)
            edge_data_2 = graph.get_edge_data(dst, src)

            new_edges[(src, dst)] = []
            for key, value in edge_data_1.items():
                # If a given weight also exists in the opposite edge, store the max of both
                dependency_types = {'EXTENDS': 4,
                                    'IMPLEMENTS': 3, 'STATIC': 2, 'METHOD_CALL': 1, 'NORMAL': 0}

                if key in edge_data_2:
                    if key == 'dependency_type':
                        dep_type_1 = dependency_types[value]
                        dep_type_2 = dependency_types[edge_data_2[key]]
                        new_edges[(src, dst)].append(
                            (key, value if dep_type_1 > dep_type_2 else edge_data_2[key]))
                    else:
                        new_edges[(src, dst)].append(
                            (key, max(value, edge_data_2[key])))
                        # If the given weight only belongs to this key,
                else:
                    new_edges[(src, dst)].append((key, value))

            # Add the remaining keys from edge_data_2 not present in edge_data_1
            for key, value in edge_data_2.items():
                if key not in edge_data_1.keys():
                    new_edges[(src, dst)].append((key, value))

        # Finally add all the edges to the graph
        for (src, dst), weights in new_edges.items():
            G.add_edge(src, dst, **{weight[0]: weight[1]
                                    for weight in weights})

        return G

    @staticmethod
    def add_edges_dependencies(curr_classe, classes, dependencies, graph, dependency_type):
        for dependency_name in dependencies:
            qualified_name = curr_classe.get_qualified_name()

            try:
                # TODO : Go back to reconsidering the type of dependency
                # ('CLASS_NAME', '{TYPE}')  TYPE = {'EXTENDS', 'IMPLEMENTS', 'NORMAL'}

                # Ignore duplicates (when a class references itself)
                if qualified_name == dependency_name or dependency_name not in classes:
                    continue

                edge_data = graph.get_edge_data(
                    qualified_name, dependency_name)

                if edge_data:
                    # Always incremenent the structural component which represents an accumulative sum of all dependencies
                    graph[qualified_name][dependency_name][str(
                        WeightType.STRUCTURAL)] = edge_data.get(str(WeightType.STRUCTURAL), 0) + 1

                    if dependency_type == 'METHOD_CALL':
                        graph[qualified_name][dependency_name][str(
                            WeightType.METHOD_CALL)] = edge_data.get(str(WeightType.METHOD_CALL), 0) + 1

                    # TODO : reconsider this due to new changes
                    # We will not update the type because the first time we set it, it will be set for
                    # EXTENDS or IMPLEMENTs which have higher priority
                else:
                    args = {'weight_structural': 1,
                            'dependency_type': dependency_type}
                    if dependency_type == 'METHOD_CALL':
                        args[str(WeightType.METHOD_CALL)] = 1

                    graph.add_edge(qualified_name,
                                   dependency_name, **args)

            except KeyError:
                # This should only happen when looking for classes that aren't explicly definied in the project
                # instead belong to framewors or external libraries
                logging.error(
                    f"Key not found for {dependency_name} at {qualified_name}")

                # This exception can cause a node to not be added. Verify and add if needed
                if not graph.has_node(qualified_name):
                    graph.add_node(qualified_name)

    @staticmethod
    def normalize_values(graph, dependency_type):
        min = sys.maxsize
        max = -sys.maxsize - 1
        for src, dst in graph.edges():
            edge_data = graph.get_edge_data(src, dst)
            if dependency_type in edge_data:
                edge = edge_data[dependency_type]
                if edge < min:
                    min = edge
                if edge > max:
                    max = edge

        for src, dst in graph.edges():
            edge_data = graph.get_edge_data(src, dst)

            if dependency_type in edge_data:
                edge = edge_data[dependency_type]
                edge = (edge - min) / (max - min)

                graph[src][dst][dependency_type] = edge
        return graph
