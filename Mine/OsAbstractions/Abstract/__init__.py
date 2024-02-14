from Mine.OsAbstractions.Abstract.Backend import AbsBackend

from Mine.OsAbstractions.Abstract.EventApi import EventApi

from Mine.OsAbstractions.Abstract.Mouse import AbsMouse
from Mine.OsAbstractions.Abstract.Keyboard import AbsKeyboard



"""
# class hierarchy

backend:
    event handler
        handles all user events
        
    state mgr
        gets / stores the state of keyboard / mouse
    
    keyboard / mouse
        send input / get state
        
    layout
        find out the data of the layout
"""