# Questionnaire2024 デプロイ手順書

## 前提条件

- Ubuntu 20.04+ / Debian 11+
- Python 3.10+
- nginx
- Git


## 1. ソースコードの取得

```bash
cd /srv
git clone <repository-url> Questionnaire2024
cd Questionnaire2024
```


## 2. Python仮想環境のセットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` に含まれていないが必要なパッケージ:

```bash
pip install uwsgi
pip install django-ckeditor-5
pip install django-extensions
pip install django-easy-audit
pip install django-debug-toolbar
pip install django-allauth
```

バージョンを固定したい場合は `pip freeze > requirements.lock` しておく。


## 3. 環境変数の設定

`Questionnaire2024/.env` を編集する。

```
SENDGRID_API_KEY='本番用のAPIキーに差し替える'
FROM_EMAIL='送信元メールアドレス'
```

`.env` は `.gitignore` に入れておくこと。


## 4. settings.py の本番設定

`Questionnaire2024/settings.py` を直接書き換える。
本番では最低限以下の変更が必要。

```python
# デバッグを無効化
DEBUG = False

# 本番ドメインを指定
ALLOWED_HOSTS = ['example.com', 'www.example.com']

# SECRET_KEY を環境変数から読み込むようにする
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-key-for-dev-only')
```

SECRET_KEY の生成:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

debug_toolbar は本番では外す。`INSTALLED_APPS` と `MIDDLEWARE` から
`debug_toolbar` 関連の行をコメントアウトまたは削除する。


## 5. データベースの初期化

本プロジェクトはSQLite3を使っている（`question.sqlite3`）。
小規模利用であればそのまま使える。
ユーザー数が多くなる場合はPostgreSQLへの移行を検討する。

```bash
# マイグレーション
python3 manage.py makemigrations
python3 manage.py migrate

# キャッシュテーブル作成（セッション管理に必要）
python3 manage.py createcachetable

# 管理者ユーザー作成
python3 manage.py createsuperuser
```


## 6. 静的ファイルの収集

```bash
python3 manage.py collectstatic --noinput
```

静的ファイルは `static/` ディレクトリに集約される。


## 7. uWSGI の設定

プロジェクトルートに `uwsgi.ini` を作成する。

```ini
[uwsgi]
chdir           = /srv/Questionnaire2024
module          = Questionnaire2024.wsgi:application
home            = /srv/Questionnaire2024/venv

master          = true
processes       = 4
threads         = 2

socket          = /tmp/questionnaire.sock
chmod-socket    = 666
vacuum          = true

max-requests    = 5000
harakiri        = 60

logto           = /var/log/uwsgi/questionnaire.log

# 環境変数
env = DJANGO_SETTINGS_MODULE=Questionnaire2024.settings
```

ログディレクトリを作成:

```bash
sudo mkdir -p /var/log/uwsgi
sudo chown www-data:www-data /var/log/uwsgi
```


## 8. systemd サービスの登録

`/etc/systemd/system/questionnaire.service` を作成する。

```ini
[Unit]
Description=Questionnaire2024 uWSGI Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/Questionnaire2024
ExecStart=/srv/Questionnaire2024/venv/bin/uwsgi --ini uwsgi.ini
Restart=on-failure
RestartSec=5
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable questionnaire
sudo systemctl start questionnaire
```


## 9. nginx の設定

`/etc/nginx/sites-available/questionnaire` を作成する。

```nginx
server {
    listen 80;
    server_name example.com;

    client_max_body_size 10M;

    location /static/ {
        alias /srv/Questionnaire2024/static/;
        expires 30d;
        access_log off;
    }

    location /media/ {
        alias /srv/Questionnaire2024/media/;
        expires 7d;
        access_log off;
    }

    location / {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/questionnaire.sock;
        uwsgi_read_timeout 60;
    }
}
```

有効化して再起動:

```bash
sudo ln -s /etc/nginx/sites-available/questionnaire /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```


## 10. 動作確認

```bash
# uWSGI の状態確認
sudo systemctl status questionnaire

# nginx の状態確認
sudo systemctl status nginx

# ログの確認
tail -f /var/log/uwsgi/questionnaire.log
tail -f /var/log/nginx/error.log
```

ブラウザで `http://example.com/survey/` にアクセスして画面が表示されれば完了。
管理画面は `http://example.com/admin/` からアクセスできる。


## よく使うコマンド

```bash
# 仮想環境の有効化
source /srv/Questionnaire2024/venv/bin/activate

# アプリの再起動
sudo systemctl restart questionnaire

# nginx の再起動
sudo systemctl restart nginx

# uWSGI プロセスの強制停止（非常時のみ）
sudo killall -9 uwsgi

# マイグレーションの再実行
python3 manage.py makemigrations
python3 manage.py migrate

# データベースの再作成（全データ消える）
rm question.sqlite3
python3 manage.py migrate
python3 manage.py createcachetable
python3 manage.py createsuperuser
```


## デプロイ時の注意事項

- `question.sqlite3` はデータ本体なので、`rm` する前にバックアップを取ること
- `DEBUG = True` のまま本番公開すると、エラー時にソースコードやDBの構造が外部に見える
- SendGrid の APIキー は `.env` で管理し、リポジトリにコミットしない
- `ALLOWED_HOSTS = ['*']` は開発用。本番では必ずドメインを指定する
- SSL化する場合は certbot (Let's Encrypt) を使う:
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d example.com
  ```


## ディレクトリ構成（本番）

```
/srv/Questionnaire2024/
  ├── venv/                    # Python仮想環境
  ├── Questionnaire2024/       # Django設定
  │   ├── settings.py
  │   ├── urls.py
  │   ├── wsgi.py
  │   └── .env                 # 環境変数（git管理外）
  ├── survey/                  # メインアプリ
  ├── dashboards/              # 管理者アプリ
  ├── static/                  # collectstatic の出力先
  ├── media/                   # アップロードファイル
  ├── question.sqlite3         # データベース
  ├── uwsgi.ini                # uWSGI設定
  ├── requirements.txt
  └── manage.py
```
