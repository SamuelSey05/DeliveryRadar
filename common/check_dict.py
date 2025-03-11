from common.zipspec import Incident

def checkClass(v, c) -> int:

    if not isinstance(v, dict) and not issubclass(c, dict):
        return isinstance(v, c)
    
    if not isinstance(v, dict) or not issubclass(c, dict):
        return 0
    
    if not set(v.keys()).issuperset(set(c.__annotations__.keys())):
            return 0
    
    for x in c.__annotations__.keys():
        if checkClass(v[x], c.__annotations__[x]) == 0: 
            return 0
        
    if set(v.keys()) == set(c.__annotations__.keys()):
        return 1

    return 2

def checkIncident(d):
     return checkClass(d, Incident)