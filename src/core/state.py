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

from weakref import proxy

from base.event import *
from task import *
from error import *

class StateError (CoreError):
    pass

class State (Task):

    def __init__ (self, *a, **k):
        self._tasks = TaskGroup ()
        self._manager = proxy (k.pop ('state_manager'))
        self._events = EventManager ()
        super (State, self).__init__ (*a, **k)
        
    @property
    def events (self):
        return self._events
    
    @property
    def tasks (self):
        return self._tasks

    @property
    def manager (self):
        return self._manager

    def setup (self):
        pass

    def do_update (self, timer):
        self.state_update (timer)
        self._tasks.update (timer)        

    def state_update (self, timer):
        pass

    def sink (self):
        pass

    def unsink (self):
        pass
    
    def release (self):
        pass


class StateManager (Task):

    def __init__ (self):
        Task.__init__ (self)
        
        self._tasks = TaskGroup ()
        self._events = EventManager ()
        self._current_state = None
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
    
    def add (self, name, factory):
        self._state_factory [name] = factory
        return self

    def start (self, name):
        if self._state_stack:
            raise StateError ('State manager already started.')
        self._push_state (self._fetch_state (name))
        self.restart ()
        
    def enter_state (self, name, *a, **k):
        self._tasks.add (lambda: self._enter_state (name, *a, **k))

    def leave_state (self):
        self._tasks.add (lambda: self._leave_state ())

    def change_state (self, name, *a, **k):
        self._tasks.add (lambda: self._change_state (name, *a, **k))
    
    def do_update (self, timer):
        self._tasks.update (timer)
        if self.current.state == Task.KILLED:
            self._leave_state ()
        if not self._state_stack:
            self.kill ()
    
    def _enter_state (self, name, *a, **k):
        state = self._fetch_state (name)
        if self._state_stack:
            self._state_stack [-1].sink ()
        self._push_state (state, *a, **k)

    def _leave_state (self):
        if not self._state_stack:
            raise StateError ('State manager empty, nothing to leave.')
        self._pop_state ()
        if self._state_stack:
            self._state_stack [-1].unsink ()
    
    def _change_state (self, name, *a, **k):
        state = self._fetch_state (name)
        self._pop_state ()
        self._push_state (state, *a, **k)
    
    def _push_state (self, state_cls, *a, **k):        
        state = state_cls (state_manager = self, *a, **k)
        self._tasks.add (state)
        self._events.connect (state.events)
        state.setup ()
        self._state_stack.append (state)

    def _pop_state (self):
        state = self._state_stack.pop ()
        self._events.disconnect (state.events)
        state.kill ()
        state.release ()
        
    def _fetch_state (self, name):
        try:
            return self._state_factory [name]
        except Exception:
            raise StateError ("Unknown state " + name)
