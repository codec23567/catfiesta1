from flask import Flask, request
# 크롤링 엔진
from regex_test import extract_images
from nickdate_test import extract_nickdate
# 게시/수정 엔진
from login_modify_actual import modify_post
from login_normal_test import modify_post_editor

from concurrent.futures import ThreadPoolExecutor
import time
import traceback

app = Flask(__name__)

# ============================================
# regex_test.py
# 본문 이미지 추출
# ============================================

@app.route("/extract", methods=["POST"])
def extract():

    data = request.get_json()

    if not data or "url" not in data:
        return {
            "success": False,
            "message": "URL 없음"
        }

    url = data["url"]

    try:
        start = time.time()

        images = extract_images(url)

        print(
            f"[시간] extract_images : "
            f"{time.time() - start:.2f}초",
            flush=True
        )

        return {
            "success": True,
            "images": images
        }

    except Exception as e:
        print(
            f"[오류] {e}",
            flush=True
        )

        return {
            "success": False,
            "message": str(e)
        }

# ============================================
# nickdate_test.py
# 날짜 / 작성자 추출
# ============================================

@app.route("/extract-info", methods=["POST"])
def extract_info():

    data = request.get_json()

    if not data or "urls" not in data:
        return {
            "success": False,
            "message": "URL 목록 없음"
        }

    urls = data["urls"]

    try:
        start = time.time()

        # 날짜/작성자 추출 작업을 최대 4개씩 병렬 처리
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(
                executor.map(
                    extract_nickdate,
                    urls
                )
            )

        print(
            f"[시간] extract_nickdate : "
            f"{time.time() - start:.2f}초",
            flush=True
        )

        return {
            "success": True,
            "results": results
        }

    except Exception as e:
        print(
            f"[오류] {e}",
            flush=True
        )

        return {
            "success": False,
            "message": str(e)
        }


# ============================================
# login_modify_actual.py
# 게시글 수정
# ============================================

@app.route("/modify", methods=["POST"])
def modify():

    data = request.get_json()

    if (
        not data
        or "id" not in data
        or "pw" not in data
        or "url" not in data
        or "html" not in data
    ):
        return {
            "success": False,
            "message": "필수 데이터 없음"
        }

    try:
        start = time.perf_counter()
        result = modify_post(
            data["id"],
            data["pw"],
            data["url"],
            data["html"]
        )
        
        print(
            f"[시간] modify_post : {time.perf_counter() - start:.2f}초",
            flush=True
        )

        return result

    except Exception as e:

        print(
            f"[오류] {e}",
            flush=True
        )

        return {
            "success": False,
            "message": str(e)
        }

# ============================================
# login_normal_test.py
# 게시글 수정 (일반 에디터)
# ============================================

@app.route("/modify-normal", methods=["POST"])
def modify_normal():

    data = request.get_json()

    if (
        not data
        or "id" not in data
        or "pw" not in data
        or "url" not in data
        or "text" not in data
    ):
        return {
            "success": False,
            "message": "필수 데이터 없음"
        }

    try:
        start = time.perf_counter()

        result = modify_post_editor(
            data["id"],
            data["pw"],
            data["url"],
            data["text"]
        )

        print(
            f"[시간] modify_post_editor : {time.perf_counter() - start:.2f}초",
            flush=True
        )

        return result

    except Exception as e:

        error = traceback.format_exc()

        print(error, flush=True)

        return {
            "success": False,
            "message": error
        }    

# ============================================
# 서버 상태 확인
# ============================================


@app.route("/")
def home():
    return "TEST1234"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
