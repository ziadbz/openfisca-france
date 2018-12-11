# -*- coding: utf-8 -*-

from .cache import tax_benefit_system
from openfisca_core.simulations import Simulation

situation = {
    "individus": {
        "demandeur": {
            "salaire_imposable": {
                "2017-12": 62191,
                "2018-01": 62191,
                "2018-02": 62191,
                "2018-03": 62191,
                "2018-04": 62191,
                "2018-05": 62191,
                "2018-06": 62191,
                "2018-07": 62191,
                "2018-08": 62191,
                "2018-09": 62191,
                "2018-10": 62191,
                "2018-11": 62191,
                "2018-12": 62191,
                "2016-01": 62191,
                "2016-02": 62191,
                "2016-03": 62191,
                "2016-04": 62191,
                "2016-05": 62191,
                "2016-06": 62191,
                "2016-07": 62191,
                "2016-08": 62191,
                "2016-09": 62191,
                "2016-10": 62191,
                "2016-11": 62191,
                "2016-12": 62191
            }
        }
    },
    "familles": {
        "_": {
            "parents": [
                "demandeur"
            ]
        }
    },
    "foyers_fiscaux": {
        "_": {
            "declarants": [
                "demandeur"
            ],
            "personnes_a_charge": []
        }
    },
    "menages": {
        "_": {
            "personne_de_reference": [
                "demandeur"
            ]
        }
    }
}

def test_cycle():
    simulation_actuelle = Simulation(
        tax_benefit_system=tax_benefit_system,
        simulation_json=situation,
        trace=True)

    simulation_actuelle.calculate('ass', '2018-12')
    logement_social_eligible = simulation_actuelle.calculate('logement_social_eligible', '2018-12')
    assert (logement_social_eligible == 0).all()
