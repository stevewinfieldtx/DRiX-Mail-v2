import csv,io
from app.main import EXPORT_FIELDS
def test_export_contract_round_trips_multiline_body():
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=EXPORT_FIELDS);w.writeheader();row={k:"" for k in EXPORT_FIELDS};row.update({"prospect_id":"p1","subject":"A consequence","body":"Line one\nLine two","email_number":1});w.writerow(row);out.seek(0);read=list(csv.DictReader(out))[0]
    assert read["body"]=="Line one\nLine two" and set(read)==set(EXPORT_FIELDS)
