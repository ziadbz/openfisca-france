from collections import defaultdict
from functools import reduce

import yaml
from openfisca_core.parameters import Parameter
from fuzzywuzzy import fuzz

from openfisca_france import CountryTaxBenefitSystem as FranceCountryTaxBenefitSystem
from openfisca_baremes_ipp import CountryTaxBenefitSystem as IppCountryTaxBenefitSystem

fr_tree = FranceCountryTaxBenefitSystem().parameters
ipp_tree = IppCountryTaxBenefitSystem().parameters

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

def export_yaml(data, file_path):
  with open(file_path, 'w') as file:
    file.write(yaml.dump(data))

def get_from_id(parameter_tree, id_param):
  relative_id = remove_prefix(id_param, parameter_tree.name).strip('.')
  try:
    return reduce(lambda tree, name: tree.children[name], relative_id.split('.'), parameter_tree)
  except KeyError:
    import ipdb; ipdb.set_trace()

def get_ascendants(parameter_id):
  splits = parameter_id.split('.')
  return ['.'.join(splits[:k]) for k in range(1, len(splits) + 1)]

def nb_sig_digits(x):
  x = str(x)
  return sum(map(lambda t: len(t.strip('0.')), x.split('.')))

def avg(l):
  return sum(l) / len(l)

class Matcher():

  TRIVIAL_VALUES = {None, 1, 0}

  def __init__(self, tree):
    self.tree = tree
    self.index = self.build_table(tree)

  @staticmethod
  def build_table(parameter_tree):
    table = defaultdict(lambda: defaultdict(lambda: []))
    for param in parameter_tree.get_descendants():
      if not isinstance(param, Parameter):
        continue
      for value in param.values_list:
        table[value.instant_str][value.value].append(param.name)

    return table

  @staticmethod
  def is_perfect_match(matches):
    if len(matches) != 1:
      return False
    match = list(matches.values())[0]
    return match[1] == 0 and match[2] == 0

  @staticmethod
  def compare(parameter_1, parameter_2):
    value_dict_2 = {value.instant_str: value.value for value in parameter_2.values_list}

    hits = []
    nb_hit = 0
    nb_miss = 0
    nb_na = 0

    for value in parameter_1.values_list:
      value_2 = value_dict_2.get(value.instant_str, UnboundLocalError)
      if (value.value == value_2):
        nb_hit += 1
        hits.append(value.value)
      elif (value_2 is UnboundLocalError):
        nb_na += 1
      else:
        nb_miss += 1

    nb_na += (len(value_dict_2) - nb_miss - nb_hit) # Dates in parameter_2 that were not in parametrer_1

    string_comp = fuzz.ratio(parameter_1.name, parameter_2.name)

    hits_quality = round(avg([nb_sig_digits(h) for h in hits]), 1)

    return [nb_hit, nb_miss, nb_na, string_comp, hits_quality], hits

  def get_match_candidates(self, parameter):
    return reduce(
      lambda matches, value: matches.union(self.index[value.instant_str][value.value]),
      parameter.values_list, set()
      )

  def get_matches(self, param):
    evaled_candidates = [
      {'name': match, 'score': self.compare(param, get_from_id(self.tree, match))}
      for match in self.get_match_candidates(param)
      ]

    filtered_candidates = list(filter(lambda candidate: self.filter_candidate(candidate, param), evaled_candidates))

    return {
      candidate['name']: candidate['score'][0]
      for candidate in filtered_candidates
      }

  def get_match_dict(self, tree_1):
    return {
      param.name: self.get_matches(param)
      for param in tree_1.get_descendants()
      if isinstance(param, Parameter)
      }

  def extract_unmatched_nodes(self, match_dict):
    matched_leafs = set(key for key, value in match_dict.items() if value)
    unmatched_leafs = set(key for key, value in match_dict.items() if not value)
    nodes_with_child_match = reduce(
      lambda acc, leaf: acc.union(get_ascendants(leaf)),
      matched_leafs, set()
      )
    nodes_with_unmatched_child = reduce(
      lambda acc, leaf: acc.union(get_ascendants(leaf)),
      unmatched_leafs, set()
      )
    nodes_with_no_matched_child = nodes_with_unmatched_child.difference(nodes_with_child_match)

    return [
      node
      for node in nodes_with_no_matched_child
      if not any([(asc in nodes_with_no_matched_child and asc != node) for asc in get_ascendants(node)])
      ]


  def get_match_report(self, tree_1):
    match_dict = self.get_match_dict(tree_1)
    no_match = self.extract_unmatched_nodes(match_dict)
    perfect_matches = {key:value for key, value in match_dict.items() if self.is_perfect_match(value)}
    other = {key:value for key, value in match_dict.items() if value and not self.is_perfect_match(value)}

    return {
    'perfect_matches': perfect_matches,
    'no_match': sorted(no_match),
    'other': other
    }


  def filter_candidate(self, candidate, param):
    (nb_hit, nb_miss, nb_na, string_comp, hits_quality), hits = candidate['score']
    if nb_hit == 1 and self.TRIVIAL_VALUES.issuperset(hits):
      return False
    return True
    # TODO: Raise conflict if there are mismatching values


fr_subtree = fr_tree.prestations.aides_logement
match_dict = Matcher(ipp_tree.prestations).get_match_report(fr_subtree)

export_yaml(match_dict, 'matches.yaml')
