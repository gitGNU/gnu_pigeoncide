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

"""
This modules defines functions to automatically generate classes that
provide the two endpoints the Observer design pattern, the Subject and
Listener.
"""

import new

from signal import signal
from sender import Receiver, Sender

class Naming:
    SUBJECT_CLASS_POSTFIX  = 'Subject'
    LISTENER_CLASS_POSTFIX = 'Listener'

DEFAULT_SUBJECT_DOC = \
"""
This is a subject class that groups different signals. You can
register to individual signals, but if you want to be notified by most
of them you can also an instance of %(listener)s (with the methods
corresponding to the signals that you want to receive overloaded) to
an object of this class.
"""

DEFAULT_LISTENER_DOC = \
"""
This is a listener class that can be used to receive different signals
from an instance of %(subject)s. Inherit from this and overload any
methods that you need and you will receive the events when connected
to the subject. You can use this class in combination with the
Trackable mixin.
"""


def make_observer (signals,
                   prefix = '_',
                   module = __name__,
                   subject_doc = DEFAULT_SUBJECT_DOC,
                   listener_doc = DEFAULT_LISTENER_DOC,
                   default_ret = None,
                   use_signals = True,
                   names = Naming):

    """
    This function generates two class objects corresponding to the
    Observer design pattern, and returns them as a tuple where the
    first element is the Subject and the second is the Listener. The
    generated subject instances will have a bunch of Signal objects,
    but you can also connect to all of them connecting an instance of
    the listener class that is also returned by this function. This
    allows fine-grained signal handling, but eases the task of
    receiven all the signals by just connecting one object.

    Parameters:

      - signals: This can be either an a list or a dictionary. The
        list just contains the names of the signals that you want to
        have in your observer. If you provide a diccionary, the keys
        are the signal names and the data associated to each key is
        the documentation that should go in the methods associated to
        the signal.

      - prefix: That is the prefix of the name of the classes
        generated by this method. The method will use the postfix
        defined in the names object. For example, if you just provide
        a prefix 'Widget', you will get two classes named
        'WidgetSubject' and 'WidgetListener'.

      - subject_doc: Documentation string for the subject class. This
        string can optinally contain the formatting wildcard
        %(listener) that would be substituted by the name of the
        listener class.

      - listener_doc: Documentation string for the listener class This
        string can optinally contain the formatting wildcard
        %(subject) that would be substituted by the name of the
        subject class.

      - default_ret: Default return parameter that the empty handler
        methods defined in the listener will return.

      - use_signals: If this is true, the signals contained by the
        subject will be signal.Signal objects, so you can also
        subscribe to them individually instead of using
        listeners. Otherwise, the signals will be simple methods that
        dispatch the event to the listeners. By default this is True.

      - names: Naming conventions used in the class generated by this
        methods. By the default this is the Naming class.
    """
    
    listener_cls_name = prefix + names.LISTENER_CLASS_POSTFIX
    subject_cls_name = prefix + names.SUBJECT_CLASS_POSTFIX
    
    listener = type (
        listener_cls_name,
        (Receiver,),
        { '__doc__' : listener_doc % {'subject' : subject_cls_name }
        , 'SIGNALS' : signals
        , 'DEFAULT_RETURN' : default_ret
        , '__module__' : module
        })

    _extend_observer_class (listener, _listener_make_signal)
    
    subject = type (
        subject_cls_name,
        (Sender,),
        { '__doc__' : subject_doc % {'listener' : listener_cls_name }
        , 'SIGNALS' : signals
        , 'DEFAULT_RETURN' : default_ret
        , '__module__' : module
        })

    _extend_observer_class (subject,
                            _signal_subject_make_signal if use_signals else
                            _subject_make_signal)

    return subject, listener

def _extend_observer_class (cls, build_signal_fn):
    for message in cls.SIGNALS:

        method = build_signal_fn (cls, message)
        method.__name__ = message
        if isinstance (cls.SIGNALS, dict):
            method.__doc__ = cls.SIGNALS [message]
        setattr (cls, message, method)

def _listener_make_signal (cls, name):
    return lambda self, *a, **k: cls.DEFAULT_RETURN
    
def _subject_make_signal (cls, name):
    return lambda self, *a, **k: self.send (name, a, k)

def _signal_subject_make_signal (cls, name):
    func = lambda *a, **k: None
    func.__name__ = name
    return signal (func)
