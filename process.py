import mysql.connector
from mysql.connector import Error
import requests
from PIL import Image
from io import BytesIO
from skimage.metrics import structural_similarity as ssim
import numpy as np


def fetch_photo_urls():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='yozm',  # 데이터베이스 이름
            user='root',  # 데이터베이스 사용자 이름
            password='asdf1234!'  # 데이터베이스 비밀번호
        )

        if connection.is_connected():
            print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
            cursor = connection.cursor()
            cursor.execute("SELECT id, photo_url FROM photo_tbl")
            records = cursor.fetchall()

            return records

    except Error as e:
        print("오류가 발생했습니다:", e)
        return []

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL 데이터베이스 연결이 종료되었습니다.")
            
def download_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        return img
    except Exception as e:
        print(f"이미지 다운로드 실패: {e}")
        return None

def image_similarity(img1, img2):
    img1 = img1.resize((200, 200))
    img2 = img2.resize((200, 200))

    img1 = np.array(img1)
    img2 = np.array(img2)

    img1_gray = np.dot(img1[...,:3], [0.299, 0.587, 0.114])
    img2_gray = np.dot(img2[...,:3], [0.299, 0.587, 0.114])

    return ssim(img1_gray, img2_gray, data_range=img1_gray.max() - img1_gray.min())

def find_most_similar_image(input_image_path):
    input_image = Image.open(input_image_path).convert('RGB')
    photo_records = fetch_photo_urls()

    max_similarity = -1
    most_similar_id = None

    for record in photo_records:
        db_id, photo_url = record
        db_image = download_image(photo_url)

        if db_image is not None:
            similarity = image_similarity(input_image, db_image)
            print(f"ID: {db_id}, Similarity: {similarity}")

            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_id = db_id

    return most_similar_id

def processing(filename):
    input_image_path = f'{filename}'
    most_similar_image_id = find_most_similar_image(input_image_path)
    return most_similar_image_id