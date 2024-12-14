from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask_login import LoginManager
app = Flask(__name__)

app.secret_key='secret'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/editedflight_db?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True


# Configuration
cloudinary.config(
    cloud_name = "dfi68mgij",
    api_key = "894594157357848",
    api_secret = "<your_api_secret>", # Click 'View API Keys' above to copy your API secret
    secure=True
)
VNPAY_CONFIG = {
    'vnp_TmnCode': 'RC52CA8T',
    'vnp_HashSecret': 'HA8UIHW181SUFMHZ42GN5ERAN89CA1KP',
    'vnp_Url': 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
    "vnp_ReturnUrl": "http://localhost:5000/vnpay_return"
}
# Ngân hàng
# NCB
# Số thẻ
# 9704198526191432198
# Tên chủ thẻ
# NGUYEN VAN A
# Ngày phát hành
# 07/15
# Mật khẩu OTP
# 123456
login = LoginManager(app)
db = SQLAlchemy(app=app)
