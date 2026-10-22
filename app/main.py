import Utils as utils
import networkx as nx
import argparse
import json
import os
import LDA as lda

from metrics.Metrics import Metrics
from metrics.MetricExecutor import MetricExecutor
from Graph import Graph
from WeightType import WeightType
from Clustering import Clustering
from entities.Method import Method
from entities.Class import Class
from Settings import Settings


def calculate_absolute_weights(graph, classes, weight_type=WeightType.TF_IDF):

    graph = Graph.normalize_values(graph, str(WeightType.STRUCTURAL))

    # Drawing of label explained here - https://stackoverflow.com/questions/31575634/problems-printing-weight-in-a-networkx-graph
    for src, dst in graph.edges():

        edge_data = graph[src][dst]

        # If the dependency is of type EXTENDS, IMPLEMENTS or STATIC (less common than NORMAL)
        primary_types = {'EXTENDS', 'IMPLEMENTS', 'STATIC'}

        # TODO : consider just removing the edge and adding it after clustering
        try:
            if edge_data["dependency_type"] in primary_types:
                edge_data[str(WeightType.ABSOLUTE)] = float(1)
            else:
                method_call_weight = 0
                if src in classes:
                    classe = classes[src]
                    calls_to_dst = 0
                    for method_call in classe.get_method_invocations():
                        target_class = method_call['targetClassName']
                        if dst == target_class:
                            calls_to_dst += 1

                    if len(classe.get_method_invocations()) > 0:
                        method_call_weight = calls_to_dst / \
                            len(classe.get_method_invocations())

                # TODO : REVIEW AND REMOVE, testing purposes only
                method_call_weight = 0
                edge_data[str(WeightType.ABSOLUTE)
                          ] = max(float(edge_data[str(weight_type)]), method_call_weight)  # method_call_weight
        except KeyError as e:
            # TODO : review why does this only happens on a specific case
            edge_data[str(WeightType.ABSOLUTE)] = 0
            print(f"KEY ERROR {e} {src} {dst}")


def extract_classes_information_from_parsed_json(json_dict):
    classes = {}
    for class_name in json_dict:
        curr = json_dict[class_name]
        annotations = curr['annotations']
        variables = curr['variables']
        dependencies = curr['dependencies']
        temp_methods = curr['methods']
        methods = []

        for method in temp_methods:
            new_method = Method(
                method, temp_methods[method]['parametersDataType'], temp_methods[method]['returnDataType'])
            methods.append(new_method)

        method_invocations = curr['methodInvocations']
        implemented_types = curr['implementedTypes']
        extended_types = curr['extendedTypes']

        new_class = Class(class_name, annotations, variables,
                          dependencies, methods, method_invocations,
                          implemented_types, extended_types)

        classes[class_name] = new_class

    return classes


def create_logging_folders(project_name):
    words_dir = f"{Settings.DIRECTORY}/data/words/{project_name}"
    services_dir = f"{Settings.DIRECTORY}/data/services/{project_name}"
    directories = [words_dir, services_dir]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def identify_clusters_in_project(project_name, project_path):
    create_logging_folders(project_name)
    temp_json_location = f'{Settings.DIRECTORY}/data/output.json'

    utils.execute_parser(project_path)

    # Read parsed document
    with open(temp_json_location) as json_file:
        parsed_raw_json = json.load(json_file)

    classes = extract_classes_information_from_parsed_json(
        parsed_raw_json)

    graph = nx.DiGraph()
    graph = Graph.create_dependencies(classes, graph)

    lda.apply_lda_to_classes(graph, classes)
    calculate_absolute_weights(graph, classes, weight_type=WeightType.LDA)

    # TODO : think about if the pre_processing should be done or not
    graph = Clustering.pre_process(
        graph, remove_weak_edges=False, remove_disconnected_sections=True)

    clusters_results = []
    if Settings.RESOLUTION:
        clusters, modularity = Clustering.community_detection_louvain(
            graph, resolution=Settings.RESOLUTION)
        clusters_results.append((clusters, modularity, Settings.RESOLUTION))
        Clustering.write_modularity_and_services(clusters_results)
    else:
        clusters_results = Clustering.compute_multiple_resolutions(
            graph, start=0.3, end=1.1, step=0.1)

    return clusters_results


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--project", "-p",
                        help="Project path", required=True)
    parser.add_argument("--stop_words", "-s",
                        help="Path to stopwords file")
    parser.add_argument("--k_topics", "-k",
                        help="Number of topics for given project")
    parser.add_argument("--resolution", "-r",
                        help="Resolution number parameter in Louvain community detection. A value in range of 0.3 to 1 is advised. A smaller resolution will identify smaller communities and vice versa. By default the whole range is tested and communities for each community saved.")
    parser.add_argument("--metrics", "-m",
                        help="Execute metrics for a given project name after normal parsing and execution (relative path to set root path) (At the current time it does NOT work independently from the identification process)", action="store_true")
    parser.add_argument("--draw", "-d",
                        help="Enable plotting of graphs", action="store_true")
    parser.add_argument("--lda-plotting", "-l",
                        help="Enable plotting of LDA topics", action="store_true")
    args = parser.parse_args()

    Settings.DRAW = True if args.draw else False
    Settings.LDA_PLOTTING = True if args.lda_plotting else False
    Settings.K_TOPICS = int(args.k_topics) if args.k_topics else None
    Settings.RESOLUTION = float(args.resolution) if args.resolution else None

    Settings.set_stop_words(args.stop_words)

    print(f"Setting Directory as: {Settings.DIRECTORY}")

    if args.project:
        project_name = str(args.project.split('/')[-1])
        project_path = str(args.project)
        Settings.PROJECT_PATH = project_path
        Settings.PROJECT_NAME = project_name

        # cluster_results = (clusters, modularity, resolution)
        clusters_results = identify_clusters_in_project(
            project_name, project_path)

        metrics = Metrics()
        for cluster in clusters_results:
            Settings.create_id()

            # TODO: Refactor MetricExecutor into ProcessResultOutput and MetricExecutor, currently sharing many responsabilities
            metric_executor = MetricExecutor()
            metric_executor.add_project(project_name, str(cluster[0]))
            metric_executor.dump_to_json_file()

            if args.metrics:
                # TODO: refactor
                metrics.set_metric_executor(metric_executor)
                metrics.set_cluster_results(clusters_results)
                metrics.calculate()

        if args.metrics:
            metrics.save()


main()
