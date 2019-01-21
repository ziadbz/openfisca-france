# -*- coding: utf-8 -*-

from __future__ import division

from openfisca_france.model.base import *


class ppa_rsa_tns_mensuel(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH


class ppa_rsa_tns_moyenne_trimestrielle(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):
        months = period.start.period('month', 3).offset(-2)
        return individu('ppa_rsa_tns_mensuel', months, options = [ADD]) / 3


class ppa_rsa_tns_base_ressource(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH

    def formula(individu, period, parameters):
        remainder = individu.famille('ppa_indice_du_mois_trimestre_reference', period)
        return (
            + individu('ppa_rsa_tns_moyenne_trimestrielle', period.offset(2)) * (remainder == 0)
            + individu('ppa_rsa_tns_moyenne_trimestrielle', period.offset(1)) * (remainder == 1)
            + individu('ppa_rsa_tns_moyenne_trimestrielle', period) * (remainder == 2)
            )
