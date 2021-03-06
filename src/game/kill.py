#
#  Copyright (C) 2010 Juan Pedro Bolivar Puente, Alberto Villegas Erce
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

from base.signal import weak_slot, Signal
from base.util import printfn
from ent.physical import PhysicalEntityBase
from ent.panda import ModelEntityBase
from ent.task import TaskEntity
from laser import Field
from core import task

from pandac.PandaModules import *
from direct.particles.ParticleEffect import ParticleEffect
import random

class KillableEntity (ModelEntityBase, PhysicalEntityBase, TaskEntity):
    """
    Incomplete mixin, must be combined with some form of physical
    entity and panda model entity.
    """
    kill_death_sounds = [ 'snd/electrocute-medium.wav',
                          'snd/electrocute-short.wav' ]

    def __init__ (self, *a, **k):
        super (KillableEntity, self).__init__ (*a, **k)

        self.enable_collision ()

        self.on_death = Signal ()
        self.on_collide += self.on_kill_collision

        self._smoke_particles = self.load_particles ('data/part/smoke.ptf')
        self._fire_particles  = self.load_particles ('data/part/fireish.ptf')
        self.death_sounds = map (self.load_sound, self.kill_death_sounds)
        self.is_dead = False

    def do_update (self, timer):
        super (KillableEntity, self).do_update (timer)
        # HACK!
        if not self.is_dead and self.position.getZ () < -1000.0:
            self.fuck_me ()

    @weak_slot
    def on_kill_collision (self, ev, me, other):
        if not self.is_dead and isinstance (other, Field):
            pos = ev.getContactPoint (0)
            self.fuck_me (pos)

    def fuck_me (self, pos = None):
        if not pos:
            pos = self.position

        self._model.detachNode ()
            
        node = self.entities.render
        self._smoke_particles.start (node)
        self._smoke_particles.setPos (pos + Vec3 (0, 0, 2))
        self._fire_particles.start (node)
        self._fire_particles.setPos (pos)
            
        self.entities.tasks.add (task.sequence (
            task.wait (2.),
            task.run (self._fire_particles.softStop),
            task.wait (2.),
            task.run (self._smoke_particles.softStop),
            task.wait (2.),
            task.run (self.dispose)))

        self.disable_physics ()
        random.choice (self.death_sounds).play ()
            
        self.on_death ()
        self.is_dead = True
    
    def load_particles (self, name):
        p = ParticleEffect ()
        p.loadConfig (Filename (name))
        p.setLightOff () 
        p.setTransparency (TransparencyAttrib.MAlpha) 
        p.setBin ('fixed', 0) 
        p.setDepthWrite (False)
        p.setShaderOff ()
        return p
    
    def dispose (self):
        self._smoke_particles.removeNode ()
        self._fire_particles.removeNode ()
        super (KillableEntity, self).dispose ()
