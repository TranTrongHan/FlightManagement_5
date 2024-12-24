import hmac

from flask import Flask
from urllib.parse import quote
import hashlib
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key='thisIsNOnSecret'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/flight_db?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True


# Configuration
cloudinary.config(
    cloud_name = "dkgcthbfj",
    api_key = "182735838243574",
    api_secret = "NHgnhBZO5DLGF8GMvlWtywy6AD8", # Click 'View API Keys' above to copy your API secret
    secure=True
)

VNPAY_CONFIG = {
    'vnp_TmnCode': 'JTUTARBA',
    'vnp_HashSecret': 'YGOTOHGJS772HDGA1KE690H64UK3SQTV',
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
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # hoặc máy chủ SMTP bạn sử dụng
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hintran6@gmail.com'  # Tài khoản email của bạn
app.config['MAIL_PASSWORD'] = 'kfms sxce qkbe lyub'  # Mật khẩu email
app.config['MAIL_DEFAULT_SENDER'] = 'hintran6@gmail.com'

mail = Mail(app)
login = LoginManager(app)
db = SQLAlchemy(app=app)
