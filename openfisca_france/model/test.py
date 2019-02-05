# -*- coding: utf-8 -*-

from __future__ import division


from openfisca_france.model.base import *
from openfisca_france.model.prestations.aides_logement import TypesZoneApl

class is_zone_1(Variable):
    value_type = bool
    entity = Menage
    definition_period = MONTH

    def formula(menage, period, parameters):
        # Toujours faux, car TypesZoneApl importé depuis aides_logement et TypesZoneApl du type de zone_apl sont 2 énums distincs
        return menage('zone_apl', period) == TypesZoneApl.zone_1
