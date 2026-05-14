#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-панель управления ботом (Flask-Admin).

Запуск на сервере:
    python3 admin_panel.py

Открыть в браузере:
    http://46.225.119.58:5001/admin

Пароль задаётся в таблице settings (ключ ADMIN_PASSWORD)
или через переменную окружения ADMIN_PASSWORD (по умолчанию: admin123)
"""
import os
import sqlite3

from flask import Flask, redirect, url_for, request, render_template_string, current_app
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

DB_FILE = os.path.abspath('bot_database.db')

app = Flask(__name__)
app.config['SECRET_KEY']                     = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI']        = f'sqlite:///{DB_FILE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ──────────────────────────────────────────────────────────────────────────────
# МОДЕЛИ
# ──────────────────────────────────────────────────────────────────────────────

class Worker(db.Model):
    __tablename__ = 'workers'
    user_id  = db.Column(db.BigInteger, primary_key=True)
    name     = db.Column(db.String(100))
    counter  = db.Column(db.Integer, default=0)
    prefix   = db.Column(db.String(10))
    clients  = db.relationship('Client', backref='worker', lazy=True,
                               foreign_keys='Client.employee_id')

    def __str__(self):
        return f"{self.name} ({self.user_id})" if self.name else str(self.user_id)


class Client(db.Model):
    __tablename__ = 'clients'
    id            = db.Column(db.Integer, primary_key=True)
    employee_id   = db.Column(db.BigInteger, db.ForeignKey('workers.user_id'), nullable=False)
    client_tag    = db.Column(db.String(100), nullable=False)
    group_chat_id = db.Column(db.BigInteger)
    is_active     = db.Column(db.Integer, default=1)

    def __str__(self):
        return self.client_tag or str(self.id)


class Setting(db.Model):
    __tablename__ = 'settings'
    key         = db.Column(db.String(100), primary_key=True)
    value       = db.Column(db.Text)
    description = db.Column(db.Text)

    def __str__(self):
        return self.key


class Order(db.Model):
    __tablename__ = 'orders'
    id              = db.Column(db.Integer, primary_key=True)
    worker_id       = db.Column(db.BigInteger)
    worker_name     = db.Column(db.String(100))
    anketa_id       = db.Column(db.String(50))
    client_tag      = db.Column(db.String(100))
    manager_comment = db.Column(db.Text)
    table_num       = db.Column(db.String(50))
    price           = db.Column(db.String(50))
    chrono_price    = db.Column(db.String(50))
    negotiation     = db.Column(db.String(50))
    year            = db.Column(db.String(50))
    diameter        = db.Column(db.String(50))
    wrist           = db.Column(db.String(50))
    kit             = db.Column(db.String(50))
    condition       = db.Column(db.String(50))
    material        = db.Column(db.String(50))
    rating          = db.Column(db.String(50))
    status          = db.Column(db.String(50), default='Available')
    created_at      = db.Column(db.DateTime)

    def __str__(self):
        return self.anketa_id or str(self.id)


# ──────────────────────────────────────────────────────────────────────────────
# АВТОРИЗАЦИЯ
# ──────────────────────────────────────────────────────────────────────────────

def get_admin_password():
    try:
        conn = sqlite3.connect(DB_FILE)
        row = conn.execute("SELECT value FROM settings WHERE key='ADMIN_PASSWORD'").fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return os.getenv('ADMIN_PASSWORD', 'admin123')


LOGIN_PAGE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Bot Admin — Вход</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
  <style>
    body { background: #0f172a; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
    .login-card { border: none; border-radius: 16px; box-shadow: 0 8px 40px rgba(0,0,0,.6); width: 360px; overflow: hidden; }
    .login-header { background: #1e293b; padding: 20px; text-align: center; color: #64748b; font-size: .8rem; letter-spacing: .1em; text-transform: uppercase; }
    .login-body { background: #fff; padding: 32px; }
  </style>
</head>
<body>
  <div class="login-card">
    <div class="login-header">Панель управления ботом</div>
    <div class="login-body">
      <h5 class="text-center mb-4">🤖 Bot Admin</h5>
      {% if error %}<div class="alert alert-danger py-2 small">{{ error }}</div>{% endif %}
      <form method="post">
        <div class="mb-3">
          <label class="form-label text-muted small">Пароль</label>
          <input type="password" name="password" class="form-control" autofocus placeholder="Введите пароль">
        </div>
        <button type="submit" class="btn btn-primary w-100">Войти</button>
      </form>
    </div>
  </div>
</body>
</html>
'''


def is_authenticated():
    return request.cookies.get('admin_auth') == get_admin_password()


class AuthMixin:
    def is_accessible(self):
        return is_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


# ──────────────────────────────────────────────────────────────────────────────
# ГЛАВНАЯ СТРАНИЦА
# ──────────────────────────────────────────────────────────────────────────────

INDEX_TMPL = '''
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Bot Admin</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
  <style>
    body { background: #f8f9fa; }
    .navbar { background: #212529; }
    .nav-link { color: #adb5bd !important; }
    .nav-link:hover { color: #fff !important; }
  </style>
</head>
<body>
<nav class="navbar navbar-expand-lg mb-4">
  <div class="container-fluid">
    <a class="navbar-brand text-white" href="/admin/">🤖 Bot Admin</a>
    <div class="navbar-nav ms-auto">
      <a class="nav-link" href="/admin/worker/">👤 Сотрудники</a>
      <a class="nav-link" href="/admin/client/">👥 Клиенты</a>
      <a class="nav-link" href="/admin/order/">📋 Заказы</a>
      <a class="nav-link" href="/admin/setting/">⚙️ Настройки</a>
      <a class="nav-link text-danger" href="/logout">Выйти</a>
    </div>
  </div>
</nav>
<div class="container-fluid px-4">
  <h4 class="mb-4">📊 Обзор</h4>
  <div class="row g-3 mb-5">
    <div class="col-sm-4">
      <div class="card text-white bg-primary">
        <div class="card-body text-center py-3">
          <h2 class="mb-0">{{ workers_count }}</h2>
          <small>Сотрудников</small>
        </div>
      </div>
    </div>
    <div class="col-sm-4">
      <div class="card text-white bg-success">
        <div class="card-body text-center py-3">
          <h2 class="mb-0">{{ clients_count }}</h2>
          <small>Активных клиентов</small>
        </div>
      </div>
    </div>
    <div class="col-sm-4">
      <div class="card text-white bg-info">
        <div class="card-body text-center py-3">
          <h2 class="mb-0">{{ orders_count }}</h2>
          <small>Анкет всего</small>
        </div>
      </div>
    </div>
  </div>
  <h5 class="mb-3">📬 Анкеты по сотрудникам</h5>
  <div class="card">
    <div class="table-responsive">
      <table class="table table-bordered table-hover table-sm mb-0">
        <thead class="table-dark">
          <tr>
            <th>Сотрудник</th>
            <th class="text-center">Всего</th>
            <th class="text-center">Available</th>
            <th class="text-center">Sold</th>
            <th class="text-center">Другие</th>
          </tr>
        </thead>
        <tbody>
          {% for row in stats %}
          <tr>
            <td><b>{{ row.name }}</b></td>
            <td class="text-center"><span class="badge bg-secondary">{{ row.total }}</span></td>
            <td class="text-center"><span class="badge bg-success">{{ row.available }}</span></td>
            <td class="text-center"><span class="badge bg-danger">{{ row.sold }}</span></td>
            <td class="text-center"><span class="badge bg-light text-dark">{{ row.other }}</span></td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
  <p class="text-muted small mt-3">Данные в реальном времени. Для детального просмотра — <a href="/admin/order/">📋 Заказы</a></p>
</div>
</body>
</html>
'''


class SecureIndex(AuthMixin, AdminIndexView):
    @expose('/')
    def index(self):
        if not self.is_accessible():
            return redirect(url_for('login'))
        try:
            conn = sqlite3.connect(DB_FILE)
            workers_count = conn.execute("SELECT COUNT(*) FROM workers").fetchone()[0]
            clients_count = conn.execute("SELECT COUNT(*) FROM clients WHERE is_active=1").fetchone()[0]
            orders_count  = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

            # Статистика по сотрудникам
            rows = conn.execute("""
                SELECT
                    w.name,
                    COUNT(o.id)                                          AS total,
                    SUM(CASE WHEN o.status = 'Available' THEN 1 ELSE 0 END) AS available,
                    SUM(CASE WHEN o.status = 'Sold'      THEN 1 ELSE 0 END) AS sold
                FROM workers w
                LEFT JOIN orders o ON w.user_id = o.worker_id
                GROUP BY w.user_id, w.name
                ORDER BY total DESC
            """).fetchall()
            conn.close()

            stats = [
                {
                    'name':      r[0] or '—',
                    'total':     r[1] or 0,
                    'available': r[2] or 0,
                    'sold':      r[3] or 0,
                    'other':     (r[1] or 0) - (r[2] or 0) - (r[3] or 0),
                }
                for r in rows
            ]
        except Exception as e:
            workers_count = clients_count = orders_count = '?'
            stats = []

        return render_template_string(
            INDEX_TMPL,
            workers_count=workers_count,
            clients_count=clients_count,
            orders_count=orders_count,
            stats=stats,
        )


# ──────────────────────────────────────────────────────────────────────────────
# MODEL VIEWS
# ──────────────────────────────────────────────────────────────────────────────

def _mask_token(view, context, model, name):
    """Скрывает чувствительные значения в таблице settings."""
    val = getattr(model, name) or ''
    if model.key in ('BOT_TOKEN', 'API_HASH', 'OPENAI_API_KEY') and len(val) > 8:
        return val[:8] + '••••••••'
    return val


class WorkerView(AuthMixin, ModelView):
    column_list            = ['user_id', 'name', 'prefix', 'counter']
    form_columns           = ['user_id', 'name', 'prefix', 'counter']
    column_labels          = {
        'user_id': 'Telegram ID', 'name': 'Имя',
        'prefix':  'Префикс анкет', 'counter': 'Счётчик',
    }
    column_searchable_list = ['name']
    can_export             = True
    export_types           = ['csv']


class ClientView(AuthMixin, ModelView):
    column_list            = ['worker', 'client_tag', 'group_chat_id', 'is_active']
    form_columns           = ['employee_id', 'client_tag', 'group_chat_id', 'is_active']
    column_labels          = {
        'worker':        'Сотрудник',
        'client_tag':    'Тег клиента',
        'group_chat_id': 'ID группы/чата',
        'is_active':     'Активен',
        'employee_id':   'ID сотрудника',
    }
    column_searchable_list = ['client_tag']
    column_filters         = ['is_active', 'employee_id']
    can_export             = True
    export_types           = ['csv']
    page_size              = 50


class SettingView(AuthMixin, ModelView):
    column_list       = ['key', 'value', 'description']
    form_columns      = ['key', 'value', 'description']
    column_labels     = {
        'key':         'Параметр',
        'value':       'Значение',
        'description': 'Описание',
    }
    column_formatters = {'value': _mask_token}
    can_export        = False


class OrderView(AuthMixin, ModelView):
    can_create             = False
    can_delete             = False
    column_list            = ['anketa_id', 'worker_name', 'client_tag',
                               'table_num', 'price', 'status', 'created_at']
    column_labels          = {
        'anketa_id':    'ID анкеты',
        'worker_name':  'Сотрудник',
        'client_tag':   'Клиент',
        'table_num':    'Таблица',
        'price':        'Цена',
        'status':       'Статус',
        'created_at':   'Создано',
    }
    column_searchable_list = ['anketa_id', 'worker_name', 'client_tag']
    column_filters         = ['worker_name', 'status']
    column_default_sort    = ('created_at', True)
    can_export             = True
    export_types           = ['csv']
    page_size              = 50


# ──────────────────────────────────────────────────────────────────────────────
# FLASK ROUTES
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password', '') == get_admin_password():
            resp = redirect(url_for('admin.index'))
            resp.set_cookie('admin_auth', get_admin_password(),
                            max_age=86400 * 7, httponly=True)
            return resp
        error = 'Неверный пароль'
    return render_template_string(LOGIN_PAGE, error=error)


@app.route('/logout')
def logout():
    resp = redirect(url_for('login'))
    resp.delete_cookie('admin_auth')
    return resp


@app.route('/')
def root():
    return redirect(url_for('admin.index'))


# ──────────────────────────────────────────────────────────────────────────────
# ADMIN SETUP
# ──────────────────────────────────────────────────────────────────────────────

admin = Admin(
    app,
    name='🤖 Bot Admin',
    index_view=SecureIndex(),
)

admin.add_view(WorkerView(Worker,   db.session, name='👤 Сотрудники', category='Данные'))
admin.add_view(ClientView(Client,   db.session, name='👥 Клиенты',    category='Данные'))
admin.add_view(OrderView(Order,     db.session, name='📋 Заказы',     category='Данные'))
admin.add_view(SettingView(Setting, db.session, name='⚙️ Настройки'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("=" * 50)
    print("  Bot Admin запущен")
    print("  http://0.0.0.0:5001/admin")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
