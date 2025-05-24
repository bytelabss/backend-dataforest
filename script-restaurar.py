import os
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


dbHost = '127.0.0.1'
db = 'dataforest_bkp'
port = 5432
user = 'dataforest'
password = 'dataforest'
backup_file = 'C:\\bkp\\backup.sql'
ENV_PATH = ".env"

load_dotenv(ENV_PATH)

def restore_postgres_db(db_host, db, port, user, password, backup_file):
    try:
        process = subprocess.Popen(
            ['C:\\Program Files\\PostgreSQL\\15\\bin\\pg_restore',
            '--no-owner',
            '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user,
                                                                      password,
                                                                      db_host,
                                                                      port, db),
            backup_file],
            stdout=subprocess.PIPE
        )
        output = process.communicate()[0]
        if int(process.returncode) != 0:
            print('Command failed. Return code : {}'.format(process.returncode))

        return output
    except Exception as e:
        print("Issue with the db restore : {}".format(e))


def enviarEmail(email_destinatario):
    # Configurações
    email_remetente = os.getenv("EMAILREMETENTE")
    senha = os.getenv("SENHAAPPEMAIL")
    assunto = "Vazamento de dados pessoais"
    mensagem = "Seus dados pessoais foram vazados!"

    # Criar o e-mail
    email = MIMEMultipart()
    email['From'] = email_remetente
    email['To'] = email_destinatario
    email['Subject'] = assunto
    email.attach(MIMEText(mensagem, 'plain'))

    # Enviar
    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(email_remetente, senha)
        servidor.send_message(email)
        servidor.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


restore_postgres_db(dbHost,db,port,user,password,backup_file)

engine = create_engine(
    f"postgresql://{user}:{password}@{dbHost}:{port}/{db}", echo=True
)

engineKeys = create_engine(
    f"postgresql://dataforest:dataforest@127.0.0.1:5432/dataforest_keys", echo=True
)

chavesDescriptografia = []
usuarios = []

with engineKeys.connect() as connection2:
    results = connection2.execute(text('select user_id, encryption_key from user_keys;'))

    chavesDescriptografia = results


with engine.connect() as connection:
    results = connection.execute(text('SELECT id,email FROM users'))

    usuarios = results



for chaveDescriptografia in chavesDescriptografia:
    for usuario in usuarios:
        if str(chaveDescriptografia[0]) == str(usuario[0]):
            fernet = Fernet(chaveDescriptografia[1])

            emailDescriptografado = fernet.decrypt(usuario[1].encode("utf-8")).decode()

            enviarEmail(emailDescriptografado)
            break


