from Settings import Settings


class Metrics:

    def __init__(self, metric_executor=None, clusters_results=[]):
        self.metric_executor = metric_executor
        self.clusters_results = clusters_results
        self.metrics = []

    def calculate(self):
        # TODO: Ugly, refactor into cleaner approach
        chm, chd, ifn, irn, opn, smq, scoh, scop, cmq, ccoh, ccop = self.metric_executor.run_metrics()
        self.metrics.append((chm, chd, ifn, irn, opn, smq,
                             scoh, scop, cmq, ccoh, ccop))

    def save(self):

        # TODO: Ugly, refactor into cleaner approach
        metric_path = f"{Settings.DIRECTORY}/data/metrics/{Settings.PROJECT_NAME}_{Settings.ID}_K{Settings.K_TOPICS}.csv"
        print(f"\n\nMetric Path: {metric_path}")
        with open(metric_path, 'w+') as f:
            # TODO: Ugly, refactor into cleaner approach
            for cluster_result, metric in zip(self.clusters_results, self.metrics):
                print(f"CLUSTER RESULT:: {cluster_result}")

                line = f"{round(cluster_result[2], 2)},{metric[0]},{metric[1]},{metric[2]},{metric[3]},{metric[4]},{metric[5]},{metric[6]},{metric[7]},{metric[8]},{metric[9]},{metric[10]}, {len(cluster_result[0])}"
                f.write(f"{line}\n")

                total = metric[0] + metric[1] + metric[5] + metric[6]
                print(
                    f"Sum for resolution {round(cluster_result[2], 2)} -> {round(total,2)}")

    def set_metric_executor(self, metric_executor):
        self.metric_executor = metric_executor

    def set_cluster_results(self, clusters_results):
        self.clusters_results = clusters_results
