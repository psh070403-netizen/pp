import os
import io
import zipfile
import requests
import pandas as pd
from datetime import datetime

API_KEY = os.environ.get("DART_API_KEY")
BASE_URL = "https://opendart.fss.or.kr/api"

if not API_KEY:
    raise ValueError("DART_API_KEY가 설정되지 않았습니다.")

# 네오바이오텍 고유번호 찾기
response = requests.get(
    f"{BASE_URL}/corpCode.xml",
    params={"crtfc_key": API_KEY}
)
response.raise_for_status()

with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    xml = z.read("CORPCODE.xml")

corps = pd.read_xml(io.BytesIO(xml))
company = corps[corps["corp_name"].str.strip() == "네오바이오텍"]

if company.empty:
    raise ValueError("네오바이오텍 기업을 찾을 수 없습니다.")

corp_code = company.iloc[0]["corp_code"]

# 2010년 이후 공시 목록 수집
today = datetime.today().strftime("%Y%m%d")

response = requests.get(
    f"{BASE_URL}/list.json",
    params={
        "crtfc_key": API_KEY,
        "corp_code": corp_code,
        "bgn_de": "20100101",
        "end_de": today,
        "pblntf_ty": "A",
        "page_count": 100
    }
)
data = response.json()

if data.get("status") != "000":
    raise ValueError(data.get("message", "공시 목록 조회 실패"))

reports = pd.DataFrame(data.get("list", []))
reports.to_csv("dart_reports.csv", index=False, encoding="utf-8-sig")

# 재무제표 수집
results = []

for _, report in reports.iterrows():
    receipt_no = report["rcept_no"]
    report_code = {
        "사업보고서": "11011",
        "반기보고서": "11012",
        "1분기보고서": "11013",
        "3분기보고서": "11014"
    }

    name = report["report_nm"]

    code = next(
        (v for k, v in report_code.items() if k in name),
        None
    )

    if not code:
        continue

    year = str(report["rcept_dt"])[:4]

     for fs_div in ["CFS", "OFS"]:
            res = requests.get(
                f"{BASE_URL}/fnlttSinglAcntAll.json",
                params={
                    "crtfc_key": API_KEY,
                    "corp_code": corp_code,
                    "bsns_year": year,
                    "reprt_code": code,
                    "fs_div": fs_div
                }
            )
            result = res.json()

            if result.get("status") == "000" and result.get("list"):
                for item in result["list"]:
                    item["rcpt_no"] = receipt_no
                    item["fs_div"] = fs_div
                    results.append(item)
                break

if results:
    pd.DataFrame(results).to_csv(
        "dart_financial_data.csv",
        index=False,
        encoding="utf-8-sig"
    )

print("DART 재무자료 수집 완료")
