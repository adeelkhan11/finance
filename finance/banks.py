import json
from . import bank
import logging
import os

logger = logging.getLogger(__name__)


class Banks:
    def __init__(self, file_name):
        with open(file_name, 'r') as f:
            json_data = json.load(f)
            if 'files' in json_data:
                self.file_specs = json_data['files']
            else:
                logger.critical("Bank file definitions not found in %s.", file_name)

        self.bank = None

    def match_bank(self, column_types):
        max_score = 0
        file_spec = None
        for b in self.file_specs:
            score = self._calc_match_score(column_types, b['coltypes'])
            if score > max_score:
                max_score = score
                file_spec = b

        return file_spec

    @staticmethod
    def _calc_match_score(file_columns, bank_columns):
        if len(file_columns) != len(bank_columns):
            return 0

        score = 0
        for f, b in zip(file_columns, bank_columns):
            if f == b:
                score += 3
            elif f in ['null', 'decimal'] and b == 'nullable decimal':
                score += 1
            else:
                score -= 3
        return score

    def select_column_names(self, file_spec, bank_name=None):
        self.bank = bank.Bank(file_spec, bank_name)

    def determine_bank_account(self, column_types, file_name):

        bank_spec = self.match_bank(column_types)

        if bank_spec is None:
            logger.critical("Error: could not match bank for file %s.", file_name)
            logger.critical("Column types: %s", ', '.join(column_types))
            exit(1)

        bank_candidates = [x['name'] for x in bank_spec['banks']]

        if len(bank_candidates) == 1:
            self.select_column_names(bank_spec)
        else:
            logger.debug("Basename: %s", os.path.basename(file_name))
            file_parts = os.path.basename(file_name).split('_')

            if 'ANZ' in bank_candidates and file_parts[0][:3] == 'ANZ':
                self.select_column_names(bank_spec, 'ANZ')
            elif 'St George' in bank_candidates and file_parts[0][:3] == 'tra':
                self.select_column_names(bank_spec, 'St George')
            elif 'ING Direct' in bank_candidates and file_parts[0][:3] == 'Tra':
                self.select_column_names(bank_spec, 'ING Direct')
            elif 'Custom' in bank_candidates:
                if len(file_parts) > 2:
                    self.select_column_names(bank_spec, 'Custom')
                    self.bank.name = file_parts[0]
                    self.bank.account_name = file_parts[1]
                else:
                    logger.critical("Error: Custom file name must be {bank}_{account}_*.csv.")
                    exit(1)

        if self.bank is None:
            logger.critical("Error: could not match bank for file %s.", file_name)
            logger.critical("Column types: %s", ', '.join(column_types))
            exit(1)
        else:
            logger.info("Bank: %s", self.bank.name)
