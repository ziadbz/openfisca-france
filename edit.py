# -*- coding: utf-8 -*-

import os

from openfisca_france import CountryTaxBenefitSystem as FranceCountryTaxBenefitSystem
from functools import reduce


fr_tbs = FranceCountryTaxBenefitSystem()


def get_from_id(parameter_tree, bits):
  if isinstance(bits, str):
    bits = bits.split('.')
  return reduce(lambda tree, name: tree.children[name], bits, parameter_tree)


# src = 'prestations.aides_logement.al_charge.personne_isolee_ou_menage_seul.cas_des_colocataires_ou_des_proprietaires_1'
# dst = 'prestations.aides_logement.al_charge.personne_isolee_menage_seul.colocataires_proprietaires'


def deep_rename(src, dst):
  src_splits = src.split('.')
  dst_splits = dst.split('.')


  def deep_rename_rec(src_splits, dst_splits):
    if len(src_splits) == 0:
      return

    if src_splits[-1] != dst_splits[-1]:

      src_param = get_from_id(fr_tbs.parameters, src_splits)
      src_file = src_param.file_path
      dst_file = os.path.join(os.path.dirname(src_file), dst_splits[-1]) + os.path.splitext(src_file)[1]
      os.rename(src_file, dst_file)

    deep_rename_rec(src_splits[:-1], dst_splits[:-1])

  deep_rename_rec(src_splits, dst_splits)


# deep_rename(src, dst)



