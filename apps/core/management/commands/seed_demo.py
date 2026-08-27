"""Наполняет сайт стартовым содержимым.

    python manage.py seed_demo

Команда безопасна: ничего не удаляет, повторный запуск не создаёт дубли.
Все тексты после этого правятся в панели управления.
"""
from django.core.management.base import BaseCommand

from apps.core.models import Credential, ExperienceItem, SiteSettings
from apps.leads.models import QuestionTemplate
from apps.services.models import Service, ServiceCategory

CATEGORIES = [
    {
        "title": "Трудовое право",
        "order": 10,
        "is_team_practice": False,
        "description": "Основное направление. Веду дела от первой консультации до суда.",
        "services": [
            ("Консультация по трудовому спору", "Разбираем ситуацию, документы и варианты действий", 400, "от", "за 45 минут"),
            ("Проверка трудового договора до подписания", "Читаю договор и объясняю, что в нём для вас невыгодно", 350, "", "за документ"),
            ("Расчёт задолженности по зарплате", "Считаю недоплаченное: часы, надбавки, отпускные", 500, "от", ""),
            ("Претензия работодателю", "Готовлю и направляю письменное требование", 800, "от", ""),
            ("Сопровождение при увольнении", "Слушание, переговоры, условия расставания", None, "", "цена по ситуации"),
            ("Ведение дела в суде", "Иск, представительство, исполнение решения", None, "", "обсуждается индивидуально"),
        ],
    },
    {
        "title": "Гражданское право",
        "order": 20,
        "is_team_practice": True,
        "description": "Веду совместно с коллегами по профилю.",
        "services": [
            ("Договоры и споры по ним", "Составление, проверка, взыскание", None, "", "по договорённости"),
        ],
    },
    {
        "title": "Корпоративное право",
        "order": 30,
        "is_team_practice": True,
        "description": "Веду совместно с коллегами по профилю.",
        "services": [
            ("Сопровождение бизнеса", "Документы, отношения с сотрудниками, споры", None, "", "по договорённости"),
        ],
    },
    {
        "title": "Миграционное право",
        "order": 40,
        "is_team_practice": True,
        "description": "Веду совместно с коллегами по профилю.",
        "services": [
            ("Статус и разрешение на работу", "Подготовка документов и сопровождение", None, "", "по договорённости"),
        ],
    },
]

QUESTIONS = [
    ("Мне задерживают или не платят зарплату", "Уже больше месяца"),
    ("Меня уволили — кажется, незаконно", "Без предупреждения или без объяснения"),
    ("Не оплачивают сверхурочные и переработки", "Работаю больше, получаю столько же"),
    ("Не отпускают в отпуск или не платят отпускные", ""),
    ("Хочу проверить трудовой договор до подписания", "Пока ничего не подписала(а)"),
    ("Не выплатили выходное пособие при уходе", ""),
    ("Не понимаю свой расчётный лист", "Суммы не сходятся"),
    ("На работе давление, угрозы или травля", "Хочу понять свои права"),
    ("Меня хотят уволить — что делать прямо сейчас", "Нужен план на ближайшие дни"),
    ("Работаю без договора", "Оформления нет, а работа есть"),
]

EXPERIENCE = [
    ("2019 — сейчас", "Частная практика", "Трудовые споры", "Консультации, досудебное урегулирование, представительство в суде."),
    ("2016 — 2019", "Юрист", "Юридическая фирма", "Сопровождение работодателей и работников по трудовым вопросам."),
]

CREDENTIALS = [
    ("Диплом юриста", "Университет", "2015"),
    ("Лицензия на юридическую практику", "", "2016"),
]


class Command(BaseCommand):
    help = "Заполняет сайт стартовыми услугами, вопросами и текстами"

    def handle(self, *args, **options):
        site = SiteSettings.load()
        if not site.about:
            site.about = (
                "Занимаюсь трудовым правом: спорами о зарплате, увольнениями, "
                "переработками и всем, что связано с отношениями работника и работодателя.\n\n"
                "Работаю с людьми, которые пришли не с готовым вопросом, а с ощущением, "
                "что на работе что-то не так. Разбираться в формулировках — моя часть работы, "
                "а не ваша."
            )
            site.save()
            self.stdout.write("Настройки сайта заполнены")

        for cat_data in CATEGORIES:
            services = cat_data.pop("services")
            category, created = ServiceCategory.objects.get_or_create(
                title=cat_data["title"], defaults=cat_data
            )
            if created:
                self.stdout.write(f"Направление: {category.title}")
            for i, (title, short, price, prefix, note) in enumerate(services, start=1):
                Service.objects.get_or_create(
                    title=title,
                    defaults={
                        "category": category,
                        "short_description": short,
                        "price": price,
                        "price_prefix": prefix,
                        "price_note": note,
                        "order": i * 10,
                    },
                )

        for i, (text, hint) in enumerate(QUESTIONS, start=1):
            QuestionTemplate.objects.get_or_create(
                text=text, defaults={"hint": hint, "order": i * 10}
            )

        for i, (period, title, org, desc) in enumerate(EXPERIENCE, start=1):
            ExperienceItem.objects.get_or_create(
                period=period,
                title=title,
                defaults={"organization": org, "description": desc, "order": i * 10},
            )

        for i, (title, issuer, year) in enumerate(CREDENTIALS, start=1):
            Credential.objects.get_or_create(
                title=title, defaults={"issuer": issuer, "year": year, "order": i * 10}
            )

        self.stdout.write(self.style.SUCCESS("Готово. Тексты можно править в /admin/"))
