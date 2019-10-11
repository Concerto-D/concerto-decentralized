class GanttChart:
    def __init__(self, transitions=(), default_show_behaviors=True):
        self._transitions = dict()
        self._default_show_behaviors = default_show_behaviors
        self.add_transitions(transitions)

    @staticmethod
    def from_json(filename):
        gc = GanttChart()
        with open(filename) as f:
            import json
            readable_dict = json.load(f)
        for component, bt in readable_dict.items():
            for behavior, transitions in bt.items():
                gc.add_transitions([[component, behavior, t["name"], t["start"], t["end"]] for t in transitions])
        return gc

    def add_transition(self, component, behavior, transition_name, start_time, end_time):
        if component not in self._transitions:
            self._transitions[component] = dict()
        if behavior not in self._transitions[component]:
            self._transitions[component][behavior] = []
        self._transitions[component][behavior].append((start_time, end_time, transition_name))

    def add_transitions(self, transitions):
        for t in transitions:
            self.add_transition(*t)

    def _flat_transitions(self):
        components_list = []
        for component, bt in self._transitions.items():
            behaviors_list = []
            for behavior, transitions in bt.items():
                behaviors_list.append([(st, et, tn, behavior) for (st, et, tn) in sorted(transitions)])
            behaviors_list.sort(key=lambda x: x[0])
            behaviors_list = _flatten(behaviors_list)
            components_list.append([(st, et, tn, bv, component) for (st, et, tn, bv) in behaviors_list])
        components_list.sort(key=lambda x: x[0])
        components_list = _flatten(components_list)
        return components_list

    def get_plotly(self, title="", show_behaviors=None, override_time_format=None):
        """ Timeformat: https://github.com/d3/d3-time-format/blob/master/README.md """
        import plotly.figure_factory as ff
        from random import randint
        from datetime import datetime

        if show_behaviors is None:
            show_behaviors = self._default_show_behaviors

        def _to_time(nb_seconds):
            return datetime.fromtimestamp(nb_seconds)

        colors = [
            '#1f77b4',  # muted blue
            '#ff7f0e',  # safety orange
            '#2ca02c',  # cooked asparagus green
            '#d62728',  # brick red
            '#9467bd',  # muted purple
            '#8c564b',  # chestnut brown
            '#e377c2',  # raspberry yogurt pink
            '#7f7f7f',  # middle gray
            '#bcbd22',  # curry yellow-green
            '#17becf'   # blue-teal
        ]
        while len(self._transitions) > len(colors):
            colors.append(f'rgb({randint(0,220)}, {randint(0,220)}, {randint(0,220)})')
        # for component_name in self._transitions:
        #     colors[component_name] = f'rgb({randint(0,256)}, {randint(0,256)}, {randint(0,256)})'

        def _name_for_trans(t):
            if show_behaviors:
                return "%s.%s.%s" % (t[4], t[3], t[2])
            else:
                return "%s.%s" % (t[4], t[2])
        df = [dict(Task=_name_for_trans(t), Start=_to_time(t[0]), Finish=_to_time(t[1]), Component=t[4]) for t in self._flat_transitions()]

        fig = ff.create_gantt(df,
                              title=title,
                              index_col='Component',
                              group_tasks=True,
                              colors=colors,
                              showgrid_x=True,
                              showgrid_y=True)

        max_time = max([_to_time(t[1]) for t in self._flat_transitions()])
        if override_time_format:
            fig.layout.xaxis.tickformat = override_time_format
        elif max_time < datetime.fromtimestamp(60):
            fig.layout.xaxis.tickformat = '%S.%L'
        elif max_time < datetime.fromtimestamp(60*60):
            fig.layout.xaxis.tickformat = '%M:%S'
        elif max_time < datetime.fromtimestamp(24*60*60):
            fig.layout.xaxis.tickformat = '%H:%M:%S'
        elif max_time < datetime.fromtimestamp(365*24*60*60):
            fig.layout.xaxis.tickformat = '%j %H:%M:%S'
        else:
            raise Exception("Error: maximum time is higher than 365 days, please provide a custom time format!")
        return fig

    def show_plotly(self, title="", show_behaviors=None, override_time_format=None):
        """ Timeformat: https://github.com/d3/d3-time-format/blob/master/README.md """
        fig = self.get_plotly(title, show_behaviors=show_behaviors, override_time_format=override_time_format)
        fig.show()

    def export_plotly(self, filename, title="", show_behaviors=None, override_time_format=None):
        """
        Supported file formats: PNG, JPEG, WebP, SVG, PDF
        Timeformat: https://github.com/d3/d3-time-format/blob/master/README.md
        """
        fig = self.get_plotly(title, show_behaviors=show_behaviors, override_time_format=override_time_format)
        fig.write_image(filename)

    def html_export_plotly(self, filename_no_ext, title="", show_behaviors=None, override_time_format=None, **kwargs):
        from plotly.offline import plot
        fig = self.get_plotly(title,
                              show_behaviors=show_behaviors,
                              override_time_format=override_time_format)
        plot(fig,
             image='svg',
             filename=filename_no_ext + ".html",
             image_filename=filename_no_ext,
             auto_open=False,
             **kwargs)

    def export_json(self, filename):
        readable_dict = dict()
        for component, bt in self._transitions.items():
            readable_dict[component] = dict()
            for behavior, transitions in bt.items():
                readable_dict[component][behavior] = [{"name": tn, "start": st, "end": et} for (st, et, tn) in sorted(transitions)]

        with open(filename, "w") as f:
            import json
            json.dump(readable_dict, f, indent='\t')

    def import_json(self, filename):
        with open(filename) as f:
            import json
            self._transitions = json.load(f)


def _flatten(list_of_lists):
    from itertools import chain
    return chain(*list_of_lists)


def _unit_tests():
    print("Running unit tests")
    gc = GanttChart()
    gc.add_transition("client", "deploy", "download", 0, 5)
    gc.add_transition("client", "deploy", "mount", 0, 0.5)
    gc.add_transition("client", "deploy", "prepare", 0.5, 3)
    gc.add_transition("client", "deploy", "configure", 4, 5)
    gc.add_transition("client", "deploy", "run", 6, 8)
    gc.add_transition("server", "deploy", "download", 0, 5)
    gc.add_transition("server", "deploy", "allocate", 0, 4)
    gc.add_transition("server", "deploy", "run", 4, 5)
    gc.add_transition("server", "deploy", "check1", 5, 6)
    gc.add_transition("server", "deploy", "check2", 5, 5.5)
    gc.add_transition("server", "deploy", "ctest", 7, 21)
    gc.show_plotly(show_behaviors=False)


if __name__ == '__main__':
    _unit_tests()
