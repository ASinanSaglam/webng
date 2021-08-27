import sys, yaml
from webng.analysis import weAverage, weEvolution, weCluster, weNetwork


class weAnalysis:
    """
    This is the core analysis class that will be used by the command line
    tool when called with the subcommand `webng analysis`.

    The class needs the analysis dictionary from the configuration file
    for initialization and when you use the `run` method it will go through
    the dictionary, calling the appropriate analysis tools with the subdictionaries
    of each, in the appropriate order.
    """

    def __init__(self, args) -> None:
        with open(args.opts, "r") as f:
            opt_dict = yaml.load(f)
        self.opts = opt_dict

    def _getd(self, dic, key, default=None, required=True):
        val = dic.get(key, default)
        if required and (val is None):
            sys.exit("{} is not specified in the dictionary".format(key))
        return val

    def run(self) -> None:
        if "analyses" in self.opts:
            print("running analyses")
            # we got some analyses to run
            analysis_dict = self.opts["analyses"]
            if "work-path" in analysis_dict:
                work_path = analysis_dict["work-path"]
            else:
                work_path = None
            #
            if self._getd(analysis_dict, "enabled", default=True):
                # we should run the analyses we have
                analysis_list = list(analysis_dict.keys())
                if "average" in analysis_list:
                    avg_dict = analysis_dict["average"]
                    if self._getd(avg_dict, "enabled", default=True):
                        print("running analysis: average")
                        # enabled, run
                        avg_dict["pcoords"] = self.opts["propagator_options"]["pcoords"]
                        avg_dict["sim_name"] = self.opts["path_options"]["sim_name"]
                        avg_dict["work-path"] = work_path
                        weAverage(avg_dict).run()
                if "evolution" in analysis_list:
                    evo_dict = analysis_dict["evolution"]
                    if self._getd(evo_dict, "enabled", default=True):
                        print("running analysis: evolution")
                        # enabled, run
                        evo_dict["pcoords"] = self.opts["propagator_options"]["pcoords"]
                        evo_dict["sim_name"] = self.opts["path_options"]["sim_name"]
                        evo_dict["work-path"] = work_path
                        weEvolution(evo_dict).run()
                if "cluster" in analysis_list:
                    clust_dict = analysis_dict["cluster"]
                    if self._getd(clust_dict, "enabled", default=True):
                        print("running analysis: cluster")
                        # enabled, run
                        clust_dict["pcoords"] = self.opts["propagator_options"][
                            "pcoords"
                        ]
                        clust_dict["sim_name"] = self.opts["path_options"]["sim_name"]
                        clust_dict["work-path"] = work_path
                        weCluster(clust_dict).run()
                if "network" in analysis_list:
                    net_dict = analysis_dict["network"]
                    if self._getd(net_dict, "enabled", default=True):
                        print("running analysis: network")
                        # enabled, run
                        if "cluster" in analysis_dict:
                            net_dict["assignments"] = analysis_dict["cluster"][
                                "assignments"
                            ]
                            net_dict["metastable-states-file"] = analysis_dict[
                                "cluster"
                            ]["metastable-states-file"]
                        net_dict["pcoords"] = self.opts["propagator_options"]["pcoords"]
                        net_dict["sim_name"] = self.opts["path_options"]["sim_name"]
                        net_dict["work-path"] = work_path
                        weNetwork(net_dict).run()
