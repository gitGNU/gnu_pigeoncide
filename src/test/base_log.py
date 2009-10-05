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

import unittest
from StringIO import StringIO

from base.log import *

class TestLog (unittest.TestCase):

    def setUp (self):
        self.info_out  = StringIO ()
        self.error_out = StringIO ()

        self.node = LogNode ()
        self.node.name = "test"
        self.node.add_listener (
            StdLogListener (LOG_INFO,
                            self.info_out,
                            self.error_out))

    def test_message (self):
        msg_one = "[test.a.b] INFO: test one\n"
        msg_two = "[test.a.b] FATAL: test two\n"

        self.node.get_path ('a.b').log (LOG_INFO, "test one")
        self.node.get_path ('a.b').log (LOG_FATAL, "test two")
        self.node.get_path ('a.b').log (LOG_DEBUG, "test three")
        
        self.assertEqual (self.info_out.getvalue (), msg_one)
        self.assertEqual (self.error_out.getvalue (), msg_two)

