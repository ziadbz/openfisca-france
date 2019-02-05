# -*- coding: utf-8 -*-

from __future__ import division


from openfisca_france.model.base import *
from openfisca_france.model.prestations.aides_logement import TypesZoneApl

class is_zone_1(Variable):
    value_type = bool
    entity = Menage
    definition_period = MONTH

    def formula(menage, period, parameters):
        # Cette formule ne fonctione pas, et retourne toujours faux, car TypesZoneApl importé depuis aides_logement et TypesZoneApl du type de zone_apl sont 2 énums distinctes
        return menage('zone_apl', period) == TypesZoneApl.zone_1


class is_zone_2(Variable):
    value_type = bool
    entity = Menage
    definition_period = MONTH

    def formula(menage, period, parameters):
        # Workaround avec possible_values
        zone_apl = menage('zone_apl', period)
        TypesZoneApl = zone_apl.possible_values
        return zone_apl == TypesZoneApl.zone_2
