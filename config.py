class Config:

    SECRET_KEY = 'your_secret_key'
    MONGO_URI = "mongodb://localhost:27017/AiRecruit"
    FLASK_JWT_SECRET_KEY = '7e4d21e87dd2238e8cf031df'

   # Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'chaabaniachref212@gmail.com'  # Your Gmail email address
    MAIL_PASSWORD = 'egfw khqv ufbd pyek'  # Your Gmail password
    MAIL_DEFAULT_SENDER = 'chaabaniachref212@gmail.com'  # Default sender
