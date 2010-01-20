#
#  Copyright (C) 2009 Juan Pedro Bolivar Puente, Alberto Villegas Erce
#  
#  This file is part of Pigeoncide.
#
#  Pigeoncide is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  Pigeoncide is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from weakref import ref

from base.event import *
from error import *
import task

class StateError (CoreError):
    pass

class State (task.Task):

    def __init__ (self, state_manager = None, *a, **k):
        assert state_manager != None
        super (State, self).__init__ (*a, **k)
        self._tasks = task.TaskGroup ()
        self._manager = ref (state_manager)
        self._events = EventManager ()
        
    @property
    def events (self):
        return self._events
    
    @property
    def tasks (self):
        return self._tasks

    @property
    def manager (self):
        return self._manager ()

    def do_setup (self):
        pass

    def do_update (self, timer):
        super (State, self).do_update (timer)
        self._tasks.update (timer)        

    def do_sink (self):
        pass

    def do_unsink (self):
        pass
    
    def do_release (self):
        pass


class StateManager (task.Task):

    def __init__ (self, *a, **k):
        super (StateManager, self).__init__ (*a, **k)
        
        self._tasks = task.TaskGroup ()
        self._tasks.auto_kill = False
        self._events = EventManager ()
        self._state_factory = {}
        self._state_stack = []

    @property
    def current (self):
        if self._state_stack:
            return self._state_stack [-1]
        return None

    @property
    def tasks (self):
        return self._tasks

    @property
    def events (self):
        return self._events
    
    def add_state (self, name, factory):
        self._state_factory [name] = factory
        return self

    def start (self, name, *a, **k):
        if self._state_stack:
            raise StateError ('State manager already started.')
        self._push_state (self._fetch_state (name), name, *a, **k)
        self.restart ()

    def force_finish (self):
        while self._state_stack:
            self._leave_state ()
        self.kill ()
        
    def enter_state (self, name, *a, **k):
        self._tasks.add (lambda: self._enter_state (name, *a, **k))

    def leave_state (self):
        self._tasks.add (lambda: self._leave_state ())

    def change_state (self, name, *a, **k):
        self._tasks.add (lambda: self._change_state (name, *a, **k))
    
    def do_update (self, timer):
        super (StateManager, self).do_update (timer)
        self._tasks.update (timer)
        if self.current.state == task.killed:
            self._leave_state ()
        if not self._state_stack:
            self.kill ()
    
    def _enter_state (self, name, *a, **k):
        state = self._fetch_state (name)
        if self._state_stack:
            self._state_stack [-1].do_sink ()
        self._push_state (state, name, *a, **k)

    def _leave_state (self):
        if not self._state_stack:
            raise StateError ('State manager empty, nothing to leave.')
        self._pop_state ()
        if self._state_stack:
            self._state_stack [-1].do_unsink ()
    
    def _change_state (self, name, *a, **k):
        state = self._fetch_state (name)
        self._pop_state ()
        self._push_state (state, name, *a, **k)
    
    def _push_state (self, state_cls, state_name, *a, **k):
        state = state_cls (state_manager = self, *a, **k)
        state.state_name = state_name
        self._tasks.add (state)
        self._events.connect (state.events)
        state.do_setup ()
        self._state_stack.append (state)

    def _pop_state (self):
        state = self._state_stack.pop ()
        self._events.disconnect (state.events)
        state.kill ()
        state.do_release ()
        
    def _fetch_state (self, name):
        try:
            return self._state_factory [name]
        except Exception:
            raise StateError ("Unknown state " + name)
