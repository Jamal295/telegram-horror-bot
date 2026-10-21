import logging
import os
from datetime import time as dt_time
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("horror-bot")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHAT_ID_RAW = os.getenv("CHAT_ID", "").strip()
TIMEZONE = os.getenv("TIMEZONE", "Asia/Amman").strip()
SCHEDULE_TIMES = os.getenv("SCHEDULE_TIMES", "09:00,15:00,21:00").strip()

# قصص أصلية قصيرة. أضف قصصًا جديدة بنفس التنسيق داخل القائمة.
STORIES = [
    {
        "title": "الرسالة اللي وصلت من بكرة",
        "body": "الساعة كانت 2:13 بعد نص الليل، وموبايل كريم نوّر برسالة من رقمه هو: «ما تفتحش باب الشقة». ضحك وقال أكيد حد بيهزر. بعدها بثواني، سمع خبطتين على الباب وصوت شبه صوته بيقول: «كريم، افتح… أنا برّه». بص على الموبايل تاني، لقى رسالة جديدة: «قلتلك ما تفتحش. أنا لسه جوّه الشقة»."
    },
    {
        "title": "الأوضة المقفولة",
        "body": "في بيت جدته، كان فيه باب صغير مقفول بقفل صدّي، وكل ما يسأل عنه تقول له: «دي أوضة فاضية». ليلة العزاء، سمع من ورا الباب حد بيهمس باسمه. قرّب ودانه، فسمع صوت جدته بالظبط: «إوعى تخلّيهم يدفنوني». في اللحظة دي، جاله اتصال من المستشفى بيأكد إن جدته ماتت من ساعتين."
    },
    {
        "title": "آخر أسانسير",
        "body": "ركب سامح الأسانسير لوحده وضغط على الدور السابع. الأسانسير وقف في الدور الرابع، والباب اتفتح على ممر ضلمة وفي آخره بنت واقفة ووشها للحيطة. ضغط قفل الباب بسرعة. قبل ما الباب يقفل، البنت لفت راسها من غير جسمها وقالت: «إنت نازل عندي ليه؟». سامح بص على لوحة الأدوار… الأسانسير كان بينزل للبدروم."
    },
    {
        "title": "الصورة القديمة",
        "body": "وهو بينضّف بيت أبوه، لقى صورة عائلية قديمة. كل الوجوه كانت مألوفة، إلا راجل واقف وراهم، إيده على كتف أبوه. سأل أمه عنه، فوشها اصفر وقالت: «مفيش حد كان واقف وراكم». في الليلة دي، رجع للصورة ولقى الراجل قرب خطوة، وبقى واقف وراه هو."
    },
    {
        "title": "مكالمة من الشقة الفاضية",
        "body": "كل يوم الساعة 11:11، كان حارس العمارة يسمع تليفون الشقة 12 بيرن. الشقة مقفولة من سنين، فقرر يدخل. التليفون كان مفصول من الحيطة، ومع ذلك بيرن. رفع السماعة، فسمع صوت طفل بيقول: «يا عم، افتحلي… أنا تحت السرير». بعدها مباشرة، سمع نفس الصوت جاي من وراه."
    },
    {
        "title": "الكرسي الهزاز",
        "body": "كل ليلة، كانت مريم تلاقي كرسي جدها بيتحرك لوحده قدام الشباك. قالت يمكن الهوا. ليلة قفلت الشبابيك كلها وحطت الكرسي في المخزن. صحيت على صوت خشب بيصرّ. الكرسي رجع مكانه، وعليه ورقة مكتوب فيها بخط جدها: «ما تقعديش مكاني»."
    },
    {
        "title": "المراية المتأخرة",
        "body": "لاحظت نور إن انعكاسها في المراية بيتأخر ثانية عن حركتها. قربت إيدها من الزجاج، فالانعكاس فضل ثابت. حاولت تبعد، لكن صورتها ابتسمت. نور جريت من الحمام وقفلت الباب. من الناحية التانية، سمعت صوتها هي بيهمس: «دوري أطلع أنا بقى»."
    },
    {
        "title": "الطريق الصحراوي",
        "body": "السواق شاف راجل بيشاور له في نص الطريق، فوقف يساعده. الراجل ركب وطلب منه يمشي من غير ما يبص في المراية. بعد دقائق، السواق نسي وبص. الكرسي الخلفي كان فاضي، لكن على الزجاج مكتوب من جوّه: «قلتلك ما تبصش». ولما بص قدامه، لقى نفس الراجل واقف في نص الطريق تاني."
    },
    {
        "title": "صوت في التسجيل",
        "body": "سجلت دينا صوت المطر عشان تنام عليه. لما شغلت التسجيل الصبح، سمعت صوتها بتتكلم وهي نايمة: «مش هسيبك تدخل». وبعدها صوت تاني رد: «أنا دخلت من زمان». دينا عاشت لوحدها، والباب والشبابيك كانوا مقفولين. فتحت التسجيل مرة تانية، فسمعت صوتًا قريبًا جدًا من الميكروفون يقول: «هي بتسمعنا دلوقتي»."
    },
    {
        "title": "الضيف اللي محدش شافه",
        "body": "في كل صور عيد ميلاد يوسف، كان فيه كرسي زيادة على السفرة. أهله أكدوا إن محدش قعد عليه. لما كبر وراجع الصور، لاحظ إن الكرسي بيقرب كل سنة من كرسيه. في صورة عيد ميلاده الثلاثين، الكرسي فاضي، لكن إيده هو كانت ممدودة كأنه ماسك إيد حد."
    },
    {
        "title": "الدور اللي مش موجود",
        "body": "عمارة قديمة فيها ست أدوار، لكن كل ليلة المصعد كان يعرض رقم 8 للحظة. في ليلة انقطع النور، ضغطت سارة على الزر بالغلط. الباب اتفتح على ممر نظيف وهادي، وفي آخره باب شقتها نفسها. دخلت، فوجدت نفسها نائمة على السرير. النسخة اللي على السرير فتحت عينيها وقالت: «اتأخرتي… أنا تعبت من التمثيل»."
    },
    {
        "title": "الهمس تحت السرير",
        "body": "كان آدم بيستخبى تحت السرير وهو صغير، وكان يسمع أمه تناديه من برّه. بعد سنين، رجع يزور البيت القديم وسمع نفس النداء من تحت السرير. انحنى وبص، فشاف طفل شبهه تمامًا. الطفل حط صباعه على بقه وقال: «ما تردش عليها… هي مش ماما»."
    },
]

def parse_times(value: str):
    parsed = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            hour_text, minute_text = item.split(":", 1)
            hour, minute = int(hour_text), int(minute_text)
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            parsed.append(dt_time(hour=hour, minute=minute, tzinfo=ZoneInfo(TIMEZONE)))
        except Exception as exc:
            raise ValueError(
                f"موعد غير صحيح: {item!r}. استخدم صيغة HH:MM مثل 09:00,15:00,21:00"
            ) from exc
    if not parsed:
        raise ValueError("لازم تحدد موعد نشر واحد على الأقل في SCHEDULE_TIMES.")
    return parsed

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "👻 بوت حكايات الغموض والرعب شغّال!\n\n"
        "الأوامر:\n"
        "/start - عرض الرسالة دي\n"
        "/id - معرفة رقم الجروب أو المحادثة\n"
        "/help - المساعدة\n\n"
        "القصص بتنزل تلقائيًا حسب مواعيد المشرف."
    )
    if update.effective_message:
        await update.effective_message.reply_text(message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat and update.effective_message:
        await update.effective_message.reply_text(
            f"رقم المحادثة (CHAT_ID): {chat.id}\n"
            "انسخ الرقم ده إلى متغير CHAT_ID في إعدادات الاستضافة."
        )

async def publish_story(context: ContextTypes.DEFAULT_TYPE):
    chat_id = int(CHAT_ID_RAW)
    slot = int(context.job.data)
    # اختيار ثابت حسب اليوم وموعد النشر لتجنب تكرار القصة في نفس اليوم.
    from datetime import datetime
    day_number = datetime.now(ZoneInfo(TIMEZONE)).date().toordinal()
    story_index = (day_number + slot * len(STORIES) // len(parse_times(SCHEDULE_TIMES))) % len(STORIES)
    story = STORIES[story_index]
    text = f"👁️‍🗨️ {story['title']}\n\n{story['body']}\n\n🕯️ لو كنت مكانه، كنت هتعمل إيه؟"
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        disable_web_page_preview=True,
    )
    logger.info("Published story index=%s title=%s", story_index, story["title"])

async def post_init(application: Application):
    times = parse_times(SCHEDULE_TIMES)
    for index, scheduled_time in enumerate(times):
        application.job_queue.run_daily(
            publish_story,
            time=scheduled_time,
            data=index,
            name=f"story-slot-{index + 1}",
        )
    logger.info("Scheduled %s daily posts in timezone %s", len(times), TIMEZONE)

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود في متغيرات البيئة.")
    if not CHAT_ID_RAW:
        raise RuntimeError("CHAT_ID غير موجود. أضف رقم الجروب إلى متغيرات البيئة.")
    try:
        int(CHAT_ID_RAW)
        ZoneInfo(TIMEZONE)
        parse_times(SCHEDULE_TIMES)
    except Exception as exc:
        raise RuntimeError(f"راجع إعدادات CHAT_ID أو TIMEZONE أو SCHEDULE_TIMES: {exc}") from exc

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("id", show_id))
    logger.info("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
