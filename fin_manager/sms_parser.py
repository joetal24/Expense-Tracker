import re
from datetime import date, datetime


class MoMoSMSParser:
    MTN_SENT_PATTERN = re.compile(
        r'You have sent\s+UGX\s*([\d,]+)\s+to\s+([^\.\n]+)',
        re.IGNORECASE,
    )
    MTN_RECEIVED_PATTERN = re.compile(
        r'You have received\s+UGX\s*([\d,]+)\s+from\s+([^\.\n]+)',
        re.IGNORECASE,
    )
    AIRTEL_SENT_PATTERN = re.compile(
        r'Confirmed\.\s+UGX\s*([\d,]+)\s+sent\s+to\s+(\S+)',
        re.IGNORECASE,
    )
    AIRTEL_RECEIVED_PATTERN = re.compile(
        r'You\s+received\s+UGX\s*([\d,]+)\s+from\s+([^\.\n]+)',
        re.IGNORECASE,
    )
    TXID_PATTERN = re.compile(
        r'(?:Transaction\s*ID|TxnID|Ref)[\s:]+([A-Z0-9]+)',
        re.IGNORECASE,
    )

    DATE_PATTERNS = [
        re.compile(r'on\s+(\d{1,2}/\d{1,2}/\d{4})', re.IGNORECASE),
        re.compile(r'on\s+(\d{4}-\d{2}-\d{2})', re.IGNORECASE),
        re.compile(r'(\d{1,2}\s+\w+\s+\d{4})', re.IGNORECASE),
    ]

    @staticmethod
    def _clean_amount(raw):
        return int(raw.replace(',', '').replace(' ', ''))

    @classmethod
    def _extract_date(cls, text):
        for pattern in cls.DATE_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            raw = match.group(1)
            for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d %B %Y', '%d %b %Y'):
                try:
                    return datetime.strptime(raw, fmt).date().isoformat()
                except ValueError:
                    continue
        return date.today().isoformat()

    @classmethod
    def parse(cls, sms_text):
        text = sms_text.strip()

        sent_match = cls.MTN_SENT_PATTERN.search(text)
        if sent_match:
            return {
                'transaction_type': 'expense',
                'amount': cls._clean_amount(sent_match.group(1)),
                'recipient': sent_match.group(2).strip().rstrip('.'),
                'sender': None,
                'provider': 'mtn',
                'payment_method': 'mtn',
                'transaction_id': cls._extract_tx_id(text),
                'date': cls._extract_date(text),
            }

        received_match = cls.MTN_RECEIVED_PATTERN.search(text)
        if received_match:
            return {
                'transaction_type': 'income',
                'amount': cls._clean_amount(received_match.group(1)),
                'recipient': None,
                'sender': received_match.group(2).strip().rstrip('.'),
                'provider': 'mtn',
                'payment_method': 'mtn',
                'transaction_id': cls._extract_tx_id(text),
                'date': cls._extract_date(text),
            }

        airtel_sent_match = cls.AIRTEL_SENT_PATTERN.search(text)
        if airtel_sent_match:
            return {
                'transaction_type': 'expense',
                'amount': cls._clean_amount(airtel_sent_match.group(1)),
                'recipient': airtel_sent_match.group(2).strip(),
                'sender': None,
                'provider': 'airtel',
                'payment_method': 'airtel',
                'transaction_id': cls._extract_tx_id(text),
                'date': cls._extract_date(text),
            }

        airtel_received_match = cls.AIRTEL_RECEIVED_PATTERN.search(text)
        if airtel_received_match:
            return {
                'transaction_type': 'income',
                'amount': cls._clean_amount(airtel_received_match.group(1)),
                'recipient': None,
                'sender': airtel_received_match.group(2).strip().rstrip('.'),
                'provider': 'airtel',
                'payment_method': 'airtel',
                'transaction_id': cls._extract_tx_id(text),
                'date': cls._extract_date(text),
            }

        return None

    @classmethod
    def _extract_tx_id(cls, text):
        match = cls.TXID_PATTERN.search(text)
        if match:
            return match.group(1)
        return None
