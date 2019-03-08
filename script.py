# -*- coding: utf-8 -*-

from param_tools.deep_merge import merge_parameters
from param_tools.p2y import to_yaml
from param_tools.utils import get_from_id, remove_prefix

from openfisca_france import CountryTaxBenefitSystem as FranceCountryTaxBenefitSystem
from openfisca_baremes_ipp import CountryTaxBenefitSystem as IppCountryTaxBenefitSystem

fr_tbs = FranceCountryTaxBenefitSystem()
ipp_tbs = IppCountryTaxBenefitSystem()

path = 'prestations.aides_logement.al_charge.personne_isolee_menage_seul.colocataires_proprietaires'

fr_param = get_from_id(fr_tbs.parameters, path)
ipp_param = get_from_id(ipp_tbs.parameters, path)

file_node_id = ipp_param.file_path.split('/parameters/')[-1].replace('.yaml', '').replace('/', '.')
file_node = get_from_id(ipp_tbs.parameters, file_node_id)

parent_id = '.'.join(path.split('.')[:-1])
child_name = path.split('.')[-1]
parent_node = get_from_id(ipp_tbs.parameters, parent_id)

merged = merge_parameters(ipp_param, fr_param)

parent_node.children[child_name] = merged


with open(ipp_param.file_path, 'w') as file:
  file.write(to_yaml(file_node))
