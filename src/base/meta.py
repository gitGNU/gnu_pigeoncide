#
#  Copyright (C) 2009 Juan Pedro Bolivar Puente, Alberto Villegas Erce
#  
#  This file is part of Pidgeoncide.
#
#  Pidgeoncide is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  Pidgeoncide is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


def instance_decorator (decorator):

    class Decorator (object):
        def __init__ (self, func, *args, **kws):
            self.__name__ = func.__name__
            self.__doc__ = func.__doc__
            self._func = func
            self._args = args
            self._kws = kws
            
        def __get__ (self, obj, cls = None):
            if obj is None:
                return None
            decorated = decorator (obj, self._func, *self._args, **self._kws)
            obj.__dict__[self.__name__] = decorated
            return decorated

    return Decorator


def extend_methods (cls, **kws):
    for name, new_method in kws.items ():
        if hasattr (cls, name):
            old_method = getattr (cls, name)
            if not callable (old_method):
                raise AttributeError ("Can not extend a non callable attribute")
            def extended (*args, **kw):
                new_method (*args, **kw)
                return old_method (*args, **kw)
            method = extended
        else:
            method = new_method
        setattr (cls, name, method)
    
    return cls 
