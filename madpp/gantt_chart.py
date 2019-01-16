import csv
from collections import OrderedDict

from madpp.gnuplot.gnuplot_gantt import gnuplot_file_from_list

class GanttChart():
    START = 0
    STOP = 1
    
    def __init__(self):
        self.log = []
    
    def start_transition(self,component,behavior,transition,time):
        self.log.append((self.START,component,behavior,transition,time))
    
    def stop_transition(self,component,behavior,transition,time):
        self.log.append((self.STOP,component,behavior,transition,time))
        
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
        
    #def export_gnuplot(self, file_name, title=''):
        #component_activities = OrderedDict()
        #tuple_list = []
        #id = 0
        
        #if len(self.log) is 0:
            #print("Not exporting Gnuplot: empty log.")
            #return
            
        #temp_dict = {}
        #(_,_,_,_,min_time) = self.log[0]
        #for (action,component,behavior,transition,time) in self.log:
            #if component not in component_activities:
                #component_activities[component] = OrderedDict()
            #if action is self.START:
                #if (component,behavior,transition) in temp_dict:
                    #raise Exception("GanttChart: error during export to gnuplot: action already started")
                #start_time = time-min_time
                #temp_dict[(component,behavior,transition)] = id
                #component_activities[component][id] = (component, behavior, transition, start_time)
                #id += 1
            #else:
                #if (component,behavior,transition) not in temp_dict:
                    #raise Exception("GanttChart: error during export to gnuplot: action finished before being started")
                #id_end = temp_dict[(component,behavior,transition)]
                #end_time = time-min_time
                #(_, _, _, start_time) = component_activities[component][id_end]
                #component_activities[component][id_end] = (component, behavior, transition, start_time, end_time)
                #del temp_dict[(component,behavior,transition)]
            
            #for component in component_activities:
                ##tuple_list.append("+ %s"%component, 0, 0)
                #for activity in component_activities[component]:
                    #(_, behavior, transition, start_time, end_time) = component_activities[component][activity]
                    #name = "%s.%s.%s"%(component,behavior,transition)
                    #name = name.replace("_","\\\\\\_")
                    #tuple_list.append((name,start_time,end_time))
        
        #gnuplot_file_from_list(tuple_list, file_name, title)
        
    def export_gnuplot(self, file_name, title=''):
        component_activities = []
        tuple_list = []
        
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
            else:
                if (component,behavior,transition) not in temp_dict:
                    raise Exception("GanttChart: error during export to gnuplot: action finished before being started")
                start_time = temp_dict[(component,behavior,transition)]
                end_time = time-min_time
                component_activities.append(component, behavior, start_time, end_time, transition)
                del temp_dict[(component,behavior,transition)]
                
            component_activities.sort()
            
            for (component, behavior, start_time, end_time, transition) in component_activities:
                name = "%s.%s.%s"%(component,behavior,transition)
                name = name.replace("_","\\\\\\_")
                tuple_list.append((name,start_time,end_time))
        
        gnuplot_file_from_list(tuple_list, file_name, title)
        
