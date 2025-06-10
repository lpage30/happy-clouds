import csv
from typing import Any, Dict, List

def load_rows(csv_filepath: str) -> List[Dict[str, Any]]:
    try:
        result: List[Dict[str, Any]] = list()
        with open(csv_filepath, 'r', encoding='utf-8-sig') as file:    
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                result.append(row)
        return result
    except Exception as e:
        raise Exception(str(e))

def write_rows(csv_filepath: str, rows: List[Dict[str,Any]]) -> str:
    field_names = {}
    for row in rows:
        field_names = sorted(field_names.update(set(row.keys())))
    field_names = list(field_names)
    empty_row = dict.fromkeys(field_names)
    try:
        with open(csv_filepath, 'w') as file:
            csv_writer = csv.DictWriter(file, fieldnames=field_names)
            csv_writer.writeheader()
            for row in rows:
                record = dict()
                record.update(empty_row)
                record.update(row)
                csv_writer.writerow(dict(sorted(record.entries())))
        return csv_filepath        
    except Exception as e:
        raise Exception(str(e))
