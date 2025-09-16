from hashlib import md5
from typing import Optional, Any, List, Iterable

import logging
import os
import pathlib
import subprocess
import re

from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import (
    StatementLine,
    Statement,
    InvestStatementLine,
    generate_transaction_id,
    recalculate_balance,
)

TYPE_MAPPING = {
    "ORDENES PAGO EMITIDAS EN MONEDA LOCAL": ("PAYMENT", False),
    "BIZUM": ("PAYMENT", False),
}

TYPE_PREFIXES = {
    "ADEUDO A SU CARGO": ("DIRECTDEBIT", False),
    "TRANSFERENCIAS": ("XFER", True),
    "PAGO CON TARJETA DE": ("PAYMENT", True),
    "PAGO CON TARJETA": ("PAYMENT", True),
    "COMPRA EN COMERCIO": ("PAYMENT", False),
    "CARGO POR COMPRA CON TARJETA EN": ("POS", True),
    "CARGO POR COMPRA CON TARJETA": ("POS", True),
    "CARGO POR PAGO DE IMPUESTOS - ": ("PAYMENT", True),
    "CARGO POR PAGO DE IMPUESTOS": ("PAYMENT", False),
    "ABONO POR TRANSFERENCIA": ("XFER", False),
    "RETIRADA DE EFECTIVO": ("ATM", False),
    "RET. EFEC.": ("ATM", False),
    "RET. EFECTIVO": ("ATM", False),
    "COM. RET. EFEC.": ("FEE", False),
    "ABONO BONIFICACIÓN": ("FEE", False),
    "BONIFICACIóN PROMOCIóN COMERCIAL": ("FEE", False),
}


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("BBVAPDF")


class BBVAPdfParser(StatementParser):

    date_format = "%d/%m/%Y"

    def __init__(self, path_name: str) -> None:
        super().__init__()
        self.path_name = path_name

    def strip_spaces(self, string: str):
        return " ".join(string.strip().split())

    def parse_pdf_lines(self, filepath: str):
        logging.debug(f"Parsing {filepath}")

        pdftotext = subprocess.run(
            [
                "pdftotext",
                "-layout",
                filepath,
                "/dev/stdout" if os.name != "nt" else "CON",
            ],
            capture_output=True,
            check=True,
        )
        lines = pdftotext.stdout.decode("utf-8").split("\n")

        parsed = []
        found_first_line = False
        found_start = False
        report_year = None
        start_balance = None

        item_regex = re.compile(
            r"^\s*(\d{2}/\d{2})\s+(\d{2}/\d{2})\b\s+(.*)\s+([-\d.,]+)\s+([-\d.,]+).*"
        )
        line_data = {}

        for line in lines:
            if "EXTRACTO DE " in line:
                match = re.match(r".*EXTRACTO DE \w+ (\d{4})\s+.*", line)
                if not match and len(match.groups()) > 1:
                    continue

                report_year = match.group(1)
                found_start = True
                continue

            if found_start and "SALDO ANTERIOR" in line:
                found_first_line = True

                if start_balance is None:
                    start_balance_match = re.match(r".*\s+([-\d.,]+)\b", line)
                    if start_balance_match and len(start_balance_match.groups()) > 0:
                        start_balance = self.parse_value(
                            start_balance_match.group(1), "amount"
                        )
                        logger.debug("Start balance found as %f", start_balance)
                        continue
                continue

            if not found_first_line:
                continue

            if line_data and (not line or "SALDO A SU FAVOR" in line):
                parsed.append(line_data)
                line_data = {}
                found_first_line = False
                continue

            if " HOJA " in line:
                found_first_line = False
                continue

            item_match = item_regex.match(line)
            if item_match:
                if line_data:
                    parsed.append(line_data)
                    logging.debug(line_data)
                    line_data = {}

                (op_date, value_date, description, amount, _) = item_match.groups()
                line_data["op-date"] = f"{op_date}/{report_year}"
                line_data["value-date"] = f"{value_date}/{report_year}"
                line_data["amount"] = amount
                line_data["type"] = self.strip_spaces(description)
                line_data["memo"] = ""
            else:
                stripped = self.strip_spaces(line)
                if stripped:
                    line_data["memo"] += (
                        f" {stripped}" if line_data["memo"] else stripped
                    )

        if line_data:
            logging.debug(line_data)

        return parsed

    def split_records(self) -> Iterable[List[dict]]:
        if os.path.isdir(self.path_name):
            parsed = []
            for pdf in pathlib.Path(self.path_name).glob("*.pdf"):
                parsed += self.parse_pdf_lines(pdf)
            return parsed
        else:
            return self.parse_pdf_lines(self.path_name)

    def remove_prefix(self, text, prefix):
        return text[text.lower().startswith(prefix.lower()) and len(prefix) :].lstrip()

    def parse_value(self, value: Optional[str], field: str) -> Any:
        if field == "trntype":
            mapping = TYPE_MAPPING.get(value)
            if mapping:
                return super().parse_value(mapping[0], field)

            for prefix, [tp, _] in TYPE_PREFIXES.items():
                if value.lower().startswith(prefix.lower()):
                    return super().parse_value(tp, field)

            raise TypeError(f"Unhandled type {value}")

        elif field == "memo":
            for prefix, [_, strip] in TYPE_PREFIXES.items():
                if strip:
                    value = self.remove_prefix(value, prefix)

        elif field == "amount":
            value = value.replace(".", "")

        return super().parse_value(value, field)

    def parse_record(self, line: List[dict]) -> Optional[StatementLine]:
        amount_key = "amount" if "amount" in line else "negative-amount"
        stat_line = StatementLine(
            date=self.parse_value(line["op-date"], "date"),
            memo=self.parse_value(line["type"], "memo"),
            amount=self.parse_value(line[amount_key], amount_key),
        )

        stat_line.date_user = self.parse_value(line["value-date"], "date_user")
        stat_line.trntype = self.parse_value(line["type"], "trntype")

        memo = self.parse_value(line["memo"], "memo")
        stat_line.memo += f" {memo}" if stat_line.memo else memo

        stat_line.id = generate_transaction_id(stat_line)

        logging.debug(stat_line)
        stat_line.assert_valid()

        return stat_line

    def parse(self) -> Statement:
        reader = self.split_records()

        for line in reader:
            self.cur_record += 1
            if not line:
                continue

            parsed = self.parse_record(line)
            if parsed:
                parsed.assert_valid()

                if isinstance(parsed, StatementLine):
                    self.statement.lines.append(parsed)
                elif isinstance(parsed, InvestStatementLine):
                    self.statement.invest_lines.append(parsed)

        if self.statement:
            recalculate_balance(self.statement)

            if self.statement.start_balance:
                logger.debug("Start balance: %0.2f", self.statement.start_balance)

            if self.statement.end_balance:
                logger.debug("End balance: %0.2f", self.statement.end_balance)

        return self.statement


class BBVAPdfPlugin(Plugin):
    """BBVA Pdf"""

    def get_parser(self, filename: str) -> StatementParser:
        return BBVAPdfParser(filename)
