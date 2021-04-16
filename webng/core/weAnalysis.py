import sys,yaml
from webng.analysis import weAverage, weEvolution

class weAnalysis:
    def __init__(self, opts) -> None:
        with open(opts, "r") as f:
            opt_dict = yaml.load(f)
        self.opts = opt_dict

    def _getd(self, dic, key, default=None, required=True):
        val = dic.get(key, default)
        if required and (val is None):
            sys.exit("{} is not specified in the dictionary".format(key))
        return val

    def run(self):
        if "analyses" in self.opts:
            print("running analyses")
            # we got some analyses to run
            analysis_dict = self.opts["analyses"]
            if self._getd(analysis_dict, "enabled", default=True):
                # we should run the analyses we have
                for analysis_type in analysis_dict.keys():
                    if analysis_type == "enabled": 
                        continue
                    elif analysis_type == "average":
                        avg_dict = analysis_dict["average"]
                        if self._getd(avg_dict, "enabled", default=True):
                            print("running analysis: {}".format(analysis_type))
                            # avg enabled, run
                            avg_dict["pcoords"] = self.opts["propagator_options"]["pcoords"]
                            avg_dict["sim_name"] = self.opts["path_options"]["sim_name"]
                            weAverage(avg_dict).run()
                    elif analysis_type == "evolution":
                        evo_dict = analysis_dict["evolution"]
                        if self._getd(evo_dict, "enabled", default=True):
                            print("running analysis: {}".format(analysis_type))
                            # avg enabled, run
                            evo_dict["pcoords"] = self.opts["propagator_options"]["pcoords"]
                            evo_dict["sim_name"] = self.opts["path_options"]["sim_name"]
                            weEvolution(evo_dict).run()
                    else: 
                        continue