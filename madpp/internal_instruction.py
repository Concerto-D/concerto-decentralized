from enum import Enum

from madpp.component import Component

class InternalInstruction:

    class Type(Enum):
        ADD = 0
        DEL = 1
        CONNECT = 2
        DISCONNECT = 3
        CHANGE_BEHAVIOR = 4
        WAIT = 5
        WAIT_ALL = 6
        
    def __str__(self):
        return "{type: %d, arguments: %s}"%(self.type, str(self.args))
        
    def __init__(self, type, args):
        self.type = type
        self.args = args
    
    @staticmethod
    def build_add(name : str, comp : Component):
        return InternalInstruction(
            InternalInstruction.Type.ADD,
            {
                "name": name,
                "comp": comp
            })
    
    @staticmethod
    def build_del(component_name : str):
        return InternalInstruction(
            InternalInstruction.Type.DEL,
            {
                "component_name": component_name
            })
    
    @staticmethod
    def build_connect(comp1_name : str, dep1_name : str, comp2_name : str, dep2_name : str):
        return InternalInstruction(
            InternalInstruction.Type.CONNECT,
            {
                "comp1_name": comp1_name,
                "dep1_name": dep1_name,
                "comp2_name": comp2_name,
                "dep2_name": dep2_name
            })
    
    @staticmethod
    def build_disconnect(comp1_name : str, dep1_name : str, comp2_name : str, dep2_name : str):
        return InternalInstruction(
            InternalInstruction.Type.DISCONNECT,
            {
                "comp1_name": comp1_name,
                "dep1_name": dep1_name,
                "comp2_name": comp2_name,
                "dep2_name": dep2_name
            })
    
    @staticmethod
    def build_change_behavior(component_name : str, behavior : str):
        return InternalInstruction(
            InternalInstruction.Type.CHANGE_BEHAVIOR,
            {
                "component_name": component_name,
                "behavior": behavior
            })
    
    @staticmethod
    def build_wait(component_name : str):
        return InternalInstruction(
            InternalInstruction.Type.WAIT,
            {
                "component_name": component_name
            })
    
    @staticmethod
    def build_wait_all():
        return InternalInstruction(
            InternalInstruction.Type.WAIT_ALL,
            {})
    
    def apply_to(self, assembly) -> bool:
        import time
        if self.type is InternalInstruction.Type.ADD:
            return assembly._add(self.args['name'], self.args['comp'])
        elif self.type is InternalInstruction.Type.DEL:
            return assembly._del(self.args['component_name'])
        elif self.type is InternalInstruction.Type.CONNECT:
            return assembly._connect(self.args['comp1_name'], self.args['dep1_name'], self.args['comp2_name'], self.args['dep2_name'])
        elif self.type is InternalInstruction.Type.DISCONNECT:
            return assembly._disconnect(self.args['comp1_name'], self.args['dep1_name'], self.args['comp2_name'], self.args['dep2_name'])
        elif self.type is InternalInstruction.Type.CHANGE_BEHAVIOR:
            return assembly._change_behavior(self.args['component_name'], self.args['behavior'])
        elif self.type is InternalInstruction.Type.WAIT:
            return assembly._wait(self.args['component_name'])
        elif self.type is InternalInstruction.Type.WAIT_ALL:
            return assembly._wait_all()
        else:
            raise Exception("Invalid internal instruction type")
    
