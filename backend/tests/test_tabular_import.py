import io
from fastapi import UploadFile
from openpyxl import Workbook
from app.main import _tabular,_suggest

def test_csv_real_headers_are_inspected_and_suggested():
    file=UploadFile(filename="leads.csv",file=io.BytesIO(b"Organization,Website,Decision Maker,Work Email\nAcme,https://acme.test,Ada,ada@acme.test\n"))
    headers,rows=_tabular(file)
    mapping=_suggest(headers)
    assert mapping=={"company_url":"Website","company_name":"Organization","contact_name":"Decision Maker","contact_email":"Work Email"}
    assert rows[0]["Organization"]=="Acme"

def test_xlsx_headers_and_rows_are_read():
    book=Workbook();sheet=book.active
    sheet.append(["Company","Domain","Job Title"])
    sheet.append(["Beta","https://beta.test","CTO"])
    data=io.BytesIO();book.save(data);data.seek(0)
    headers,rows=_tabular(UploadFile(filename="leads.xlsx",file=data))
    assert headers==["Company","Domain","Job Title"]
    assert rows==[{"Company":"Beta","Domain":"https://beta.test","Job Title":"CTO"}]
    assert _suggest(headers)["company_name"]=="Company"

def test_xlsx_always_uses_excel_row_one_as_headers():
    book=Workbook();sheet=book.active
    sheet.append(["Lead Website","Business","Person"])
    sheet.append(["URL","Company","Contact Name"])
    data=io.BytesIO();book.save(data);data.seek(0)
    headers,rows=_tabular(UploadFile(filename="leads.xlsx",file=data))
    assert headers==["Lead Website","Business","Person"]
    assert rows[0]["Lead Website"]=="URL"

def test_xlsx_uses_row_one_from_the_sheet_with_real_columns():
    book=Workbook();cover=book.active;cover.title="Cover"
    cover["A1"]="fram^ — Consolidated Warm-Contact List"
    leads=book.create_sheet("Prospects")
    leads.append(["Company Name","URL","Contact Name","Email"])
    leads.append(["Acme","https://acme.test","Ada","ada@acme.test"])
    data=io.BytesIO();book.save(data);data.seek(0)
    headers,rows=_tabular(UploadFile(filename="warm-list.xlsx",file=data))
    assert headers==["Company Name","URL","Contact Name","Email"]
    assert rows[0]["URL"]=="https://acme.test"

def test_empty_xlsx_is_safe():
    book=Workbook();book.active.delete_rows(1,10)
    data=io.BytesIO();book.save(data);data.seek(0)
    headers,rows=_tabular(UploadFile(filename="empty.xlsx",file=data))
    assert rows==[]
