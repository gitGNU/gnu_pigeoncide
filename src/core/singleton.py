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

class Singleton (type): 

    def __init__ (cls, name, bases, dct):
        cls.__instance = None
        type.__init__(cls, name, bases, dct)
 
    def __call__ (cls, *args, **kw):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls, *args,**kw)
        return cls.__instance
