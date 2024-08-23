# راهنمای پروژه طاقچه

این پروژه با استفاده از **Django** و **Celery** برای مدیریت عملیات‌های پس‌زمینه طراحی شده است. همچنین از **RabbitMQ** و **Redis** برای صف‌های پیام و کش داده‌ها استفاده می‌کند. در این مستند به معرفی سرویس‌ها و تنظیمات پروژه پرداخته‌ایم.

## پیش‌نیازها

برای اجرای این پروژه، نیاز به ابزارها و پیش‌نیازهای زیر دارید:

- **Docker** و **Docker Compose**
- **Python 3.8+**
- **RabbitMQ**
- **Redis**

## ساختار پروژه

پروژه از سرویس‌های مختلفی تشکیل شده است که در فایل `docker-compose.yml` تعریف شده‌اند . همچنین فایل `.env` در روت پروژه حاوی اطلاعات مهمی است که میتوانید پیش از اجرا ویرایش کنید.

### سرویس‌ها

- **django**: این سرویس به عنوان اپلیکیشن اصلی Django عمل می‌کند.
- **redis**: برای ذخیره کش‌ها استفاده می‌شود.
- **rabbitmq**: به عنوان صف پیام‌ها عمل می‌کند.
- **celery**: کارهای پس‌زمینه را اجرا می‌کند.


## راه‌اندازی پروژه

برای راه‌اندازی این پروژه، مراحل زیر را دنبال کنید:

1. **دریافت ( clone ) کردن Repo **:
   ابتدا Repo پروژه را clone کنید:
   ```bash
   git clone git@github.com:Mohammad-SS/taghche-api.git .
   ```

2. **تنظیمات محیطی**:
   فایل `.env` را با مقادیر مناسب برای تنظیمات Redis، RabbitMQ و Django ایجاد کنید.

3. **اجرای Docker Compose**:
   برای ساخت و اجرای سرویس‌ها، از دستور زیر استفاده کنید:
   ```bash
   docker compose up --build
   ```

4. **دسترسی به سرویس‌ها**:
   - برنامه Django در پورت `5000` در دسترس است.
   - رابط کاربری RabbitMQ در پورت `15672` در دسترس است.

## تست‌ها

برای اجرای تست‌های پروژه، از فریمورک **pytest** استفاده شده است. تست‌ها برای اطمینان از عملکرد صحیح سرویس‌ها و عملیات کش کتاب‌ها طراحی شده‌اند.

### اجرای تست‌ها

```bash
docker-compose exec django pytest
```

### نحوه کارکرد پروژه
این پروژه تنها یک url جهت استفاده کاربر دارد . این url به شرح زیر است
```text
http://localhost/api/book/<id:integer>
```
مقدار id را از سایت طاقچه برای کتاب های مختلف انتخاب میکنیم .

 در ابتدا ، با ورود به این صفحه از طریق API سایت طاقچه ( که در ادامه به آن upstream میگوییم ) دریافت شده و بلافاصله پس از دریافت در هر دو لایه کشینگ سیستم ذخیره میشود .
لایه پایین تر کش مموری است و لایه بالاتر کش ردیس . کش مموری 300 ثانیه یا 5 دقیقه اعتبار دارد و برای ردیس تاریخ انقضایی تعریف نشده است . البته میتوانید از طریق تنظیمات `.env` این زمان را تغییر دهید . 
پس از انقضای کش مموری ، اطلاعات مجددا از ردیس خوانده شده و در مموری ذخیره میشوند . 

 همچنین ، با توجه به اتصال rabbitmq ، مکانیزمی تعبیه شده که میتوانید در آن مقدار کش را حذف و یا رفرش کنید . این مقادیر با `celery` دریافت شده و با `api` به سیستم اصلی متصل هستند . از طریق دو متد `put` و `delete` در تنها ویو این پروژه ، این مقادیر را حذف و یا رفرش میکنند.

 همچنین ، در نظر داشته باشید برای `book` یک کلاس مجزا نوشته شده است که متد های `get` و `set` درون آن پیاده سازی شده اند.

 جهت استفاده از مسیج بروکر برای تست `celery` میتوانید از توابع کمکی استفاده کنید و یا از طریق `rabbitmq-managementui` یک مسیج در صف مورد نظر پابلیش کنید . 

## توابع کمکی

در این پروژه، از توابع کمکی برای مدیریت کش کتاب‌ها استفاده شده است. این توابع با استفاده از RabbitMQ پیام‌هایی را برای پاکسازی یا بروزرسانی کش‌ها ارسال می‌کنند.

## اطلاعات مورد نیاز جهت پابلیش مسیج

#### جهت حذف کش ها 

```text
payload = {
"task": "books.tasks.clear_book_cache" <REQUIRED>
"id": str <REQUIRED>
"kwargs": {
   "book_id": int <REQUIRED>
   "delete_from": list <OPTIONAL> , OPTIONS : ['default' , 'redis_cache']
   }
{
exchange = 'books'
routing_key = 'books.clear_cache'
content_type = 'application/json'
queue = 'cache_cleaner'
```

#### جهت رفرش کش ها 

```text
payload = {
"task": "books.tasks.refresh_book_cache" <REQUIRED>
"id": str <REQUIRED>
"kwargs": {
   "book_id": int <REQUIRED>
   "update_in": list <OPTIONAL> , OPTIONS : ['default' , 'redis_cache']
   }
{
exchange = 'books'
routing_key = 'books.refresh_cache'
content_type = 'application/json'
queue = 'cache_cleaner'
```


## پی نوشت ها : 
- کد ها با flake8 و black فرمت شدند تا مطابق pep8 باشند.
- در زمان اجرای داکر کامپوز ، حدود 10 ثانیه برای اجرای کامل ربیت و اتصال به سلری زمان لازم هست.
- در زمان اجرای تست ها ، 2 ثانیه برای پابلیش پیام در ربیت ، دریافتش در سلری و اجرای اون در جنگو زمان در نظر گرفته شده که باید منتظر باشید.
