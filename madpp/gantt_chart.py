import csv
from collections import OrderedDict

from madpp.gnuplot.gnuplot_gantt import gnuplot_file_from_list

class GanttChart():
    START = 0
    STOP = 1
    CHANGE_BEHAVIOR = 2
    
    def __init__(self):
        self.log = []
    
    def start_transition(self,component,behavior,transition,time):
        self.log.append((self.START,component,behavior,transition,time))
    
    def stop_transition(self,component,behavior,transition,time):
        self.log.append((self.STOP,component,behavior,transition,time))
    
    def change_behavior(self,component,behavior,time):
        self.log.append((self.CHANGE_BEHAVIOR, component, behavior, None, time))
        
    def dump(self, file_name):
        file = open(file_name, "w")
        
        fieldnames = ['action', 'component', 'behavior', 'transition', 'time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for (action,component,behavior,transition,time) in self.log:
            row_dict = {
                'action': action,
                'component': component,
                'behavior': behavior,
                'transition': transition,
                'time': time
            }
            writer.writerow(row_dict)
        
        file.close()
    
    def _get_ordered_tuples(self):
        transitions = []
        change_behaviors = []
        
        max_time = 0.0
        
        if len(self.log) is 0:
            print("Not exporting Gnuplot: empty log.")
            return
            
        temp_dict = {}
        (_,_,_,_,min_time) = self.log[0]
        for (action,component,behavior,transition,time) in self.log:
            if action is self.START:
                if (component,behavior,transition) in temp_dict:
                    raise Exception("GanttChart: error during export to gnuplot: action already started")
                start_time = time-min_time
                temp_dict[(component,behavior,transition)] = start_time
                if start_time > max_time: max_time = start_time
            elif action is self.STOP:
                if (component,behavior,transition) not in temp_dict:
                    raise Exception("GanttChart: error during export to gnuplot: action finished before being started")
                start_time = temp_dict[(component,behavior,transition)]
                end_time = time-min_time
                transitions.append((component, behavior, start_time, end_time, transition))
                if end_time > max_time: max_time = end_time
                del temp_dict[(component,behavior,transition)]
            else:
                start_time = time-min_time
                change_behaviors.append((component, start_time, behavior))
                if start_time > max_time: max_time = start_time
        
        next_cb_dict = {}
        new_change_behaviors = []
        for (component, start_time, behavior) in reversed(change_behaviors):
            if component in next_cb_dict:
                end_time = next_cb_dict[component]
            else:
                end_time = max_time
            if behavior is not None:
                new_change_behaviors.insert(0,(component, start_time, end_time, behavior))
            next_cb_dict[component] = start_time
        
        transitions.sort()
        new_change_behaviors.sort()
        
        return (transitions, new_change_behaviors)
        
    def get_formatted(self):
        (transitions, change_behaviors) = self._get_ordered_tuples()
        
        to_return = {
            "transitions": [],
            "behaviors": []
        }
        
        if len(transitions) > 0:
            (old_component, old_behavior, _, _, _) = transitions[0]
            component_set = []
            behavior_set = []
            for (component, behavior, start_time, end_time, transition) in transitions:
                if (component is not old_component) or (behavior is not old_behavior):
                    component_set.append({"behavior": old_behavior, "transitions": behavior_set})
                    behavior_set = []
                if component is not old_component:
                    to_return["transitions"].append({"component": old_component, "behaviors": component_set})
                    component_set = []
                behavior_set.append({"transition": transition, "start": start_time, "end": end_time})
                old_behavior = behavior
                old_component = component
            component_set.append({"behavior": old_behavior, "transitions": behavior_set})
            to_return["transitions"].append({"component": old_component, "behaviors": component_set})
            
        if len(change_behaviors) > 0:
            (old_component, _, _, _) = change_behaviors[0]
            component_set = []
            for (component, start_time, end_time, behavior) in change_behaviors:
                if component is not old_component:
                    to_return["behaviors"].append({"component": old_component, "behaviors": component_set})
                component_set.append({"behavior": behavior, "start": start_time, "end": end_time})
                old_component = old_component
            to_return["behaviors"].append({"component": old_component, "behaviors": component_set})
        
        return to_return
    
    def export_json(self, file_name):
        from json import dump
        with open(file_name, "w") as f:
            dump(self.get_formatted(), f, indent='\t')
        
    def export_gnuplot(self, file_name, title=''):
        (transitions, change_behaviors) = self._get_ordered_tuples()
        tuple_list = []
        change_behaviors_dict = {}
        
        for (component, start_time, end_time, behavior) in change_behaviors:
            if component not in change_behaviors_dict:
                change_behaviors_dict[component] = []
            change_behaviors_dict[component].append((start_time, end_time, behavior))
        
        for (component, behavior, start_time, end_time, transition) in transitions:
            if component in change_behaviors_dict:
                for (s, e, b) in change_behaviors_dict[component]:
                    tuple_list.append((component,s,e))
                del change_behaviors_dict[component]
            name = "%s.%s.%s"%(component,behavior,transition)
            name = name.replace("_","\\\\\\_")
            tuple_list.append((name,start_time,end_time))
            
        for c in change_behaviors_dict:
            for (s, e, b) in change_behaviors_dict[c]:
                tuple_list.append((c,s,e))
        
        gnuplot_file_from_list(tuple_list, file_name, title)
        
