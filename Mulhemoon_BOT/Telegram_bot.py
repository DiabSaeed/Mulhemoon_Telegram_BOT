from Slides import Slides
from Users import Users
from feedback_analyzer import Answers, FeedbackAnalyzer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.ext import CallbackContext
from telegram.error import TimedOut
from typing import Final
import aiofiles
from dotenv import load_dotenv
import os
import re
from xhtml2pdf import pisa
from io import BytesIO
import base64
import markdown

def clean_html_generator(text):
    unsupported_tags = r"(</?(p|div|span|img|table|thead|tbody|tfoot|tr|th|td|ul|ol|li|h[1-6]|style|script|blockquote|hr|iframe|form|input|button|label|select|option|textarea)[^>]*>)"
    clean_html = re.sub(unsupported_tags, "", text)
    clean_html = re.sub(r"<br\s*/?>", "\n", clean_html)
    return clean_html

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  
        u"\U0001F300-\U0001F5FF"  
        u"\U0001F680-\U0001F6FF"  
        u"\U0001F1E0-\U0001F1FF"  
        u"\U00002700-\U000027BF"  
        u"\U000024C2-\U0001F251"  
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def get_formatted_feedback(feedback):
    feedback_items = []
    for fb in feedback:
        feedback_items.append(f"<h3>Slide: {fb['name']}</h3>")
        feedback_items.append(f"<p>{fb['feedback']}</p>")
        feedback_items.append("<hr/>")
    formatted_feedback = "".join(feedback_items)
    return formatted_feedback

load_dotenv()
TOKEN: Final = os.getenv("BOT_TOKEN")
BOT_USERNAME: Final = '@mulhemoonbot'
GET_NAME, GET_ORGAN, GET_DESCRIPTION= range(3)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''أزيك أتمنى تكون بخير وبأحسن حال 
                                      البوت ده هيديك 10 اسلايدات كل اسلايد هتكتب اسمها الأول ولو اسمها صح هيعرضلك السؤال اللي بعده
                                      وهو انك تكتب الوصف بتاعها وهيحلل ردك ويقيمه ويديك نبذة عن أداءك وأزاي تحسنه 
                                      لو حسيت بتأخر في الرد شوية متقلقش الموضوع كله في سرعة النت بس مش أكتر 
                                      وربنا يوفقكم جميعا ♥
                                      اكتب /start لبداية''')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    users_db = Users("test.db")
    context.user_data['name_score'] = 0
    context.user_data['organ_score'] = 0
    context.user_data['feedback'] = []

    if user_id not in users_db.get_users():
        users_db.add_user(user_id, username, first_name, last_name)

    if 'remaining_slides' not in context.user_data:
        slides_db = Slides("test.db")
        slides_db.clear_showen()
        context.user_data['remaining_slides'] = slides_db.get_random_slides(user_id, n=10)

    if not context.user_data['remaining_slides']:
        await update.message.reply_text("""انتهى الإختبار. شكراً لمشاركتك!
                                     لو عاوزني أطلعلك تقييم لآداءك ككل في صيغة 
                                     pdf 
                                     استخدم الأمر /SendPDF""")
        analyzer = FeedbackAnalyzer()
        formatted_feedback = get_formatted_feedback(context.user_data['feedback'])
        overall_feedback = analyzer.overall_feedback(formatted_feedback)
        context.user_data['overall_feedback'] = overall_feedback
        await update_user_rate(update, context)
        return ConversationHandler.END

    slide = context.user_data['remaining_slides'].pop(0)
    context.user_data['current_slide'] = slide
    image_path = slide['image_path']
    async with aiofiles.open(image_path, 'rb') as img:
        img_bytes = await img.read()
    await update.message.reply_photo(photo=img_bytes, caption="أكتب اسم هذه الشريحة:")
    return GET_NAME

async def get_name(update: Update, context: CallbackContext):
    user_answer = update.message.text
    current_slide = context.user_data['current_slide']
    correct_name = current_slide['name']
    
    answer = Answers(correct_name, "", "")
    feedback_analyzer = FeedbackAnalyzer(answer)
    if 'name_attempts' not in context.user_data:
        context.user_data['name_attempts'] = 1
    else:
        context.user_data['name_attempts'] += 1

    if feedback_analyzer.check_name(user_answer):
        context.user_data['user_name_input'] = user_answer
        await update.message.reply_text("اسم الشريحة صحيح! الآن اكتب العضو:")
        context.user_data['name_score'] += 1
        context.user_data['name_attempts'] = 0
        return GET_ORGAN
    else:
        
        if context.user_data['name_attempts'] >= 3:
            await update.message.reply_text(f"اسم الشريحة الصحيح : {correct_name}")
            await update.message.reply_text("للأسف غلطت 3 مرات. هنروح للشريحة اللي بعدها.")
            context.user_data['name_attempts'] = 0
            if not context.user_data['remaining_slides']:
                await update.message.reply_text("""انتهى الإختبار. شكراً لمشاركتك!
                                     لو عاوزني أطلعلك تقييم لآداءك ككل في صيغة 
                                     pdf 
                                     استخدم الأمر /SendPDF""")
                analyzer = FeedbackAnalyzer()
                formatted_feedback = get_formatted_feedback(context.user_data['feedback'])
                overall_feedback = analyzer.overall_feedback(formatted_feedback)
                context.user_data['overall_feedback'] = overall_feedback
                await update_user_rate(update, context)
                return ConversationHandler.END
            slide = context.user_data['remaining_slides'].pop(0)
            context.user_data['current_slide'] = slide
            image_path = slide['image_path']
            async with aiofiles.open(image_path, 'rb') as img:
                img_bytes = await img.read()
            await update.message.reply_photo(photo=img_bytes, caption="أكتب اسم هذه الشريحة:")
            return GET_NAME
        else:
            await update.message.reply_text("الاسم غير صحيح. حاول تاني:")
            return GET_NAME
        

async def get_organ(update: Update, context: CallbackContext):
    user_answer = update.message.text
    current_slide = context.user_data['current_slide']
    correct_organ = current_slide['organ']
    answer = Answers(current_slide['name'], "", correct_organ)
    feedback_analyzer = FeedbackAnalyzer(answer)
    if 'organ_attempts' not in context.user_data:
        context.user_data['organ_attempts'] = 1
    else:
        context.user_data['organ_attempts'] += 1

    if feedback_analyzer.check_organ(user_answer):
        context.user_data['user_organ_input'] = user_answer
        await update.message.reply_text("العضو صحيح! الآن اكتب الوصف:")
        context.user_data['organ_score'] += 1
        context.user_data['organ_attempts'] = 0
        return GET_DESCRIPTION
    else:
        if context.user_data['organ_attempts'] >= 3:
            await update.message.reply_text(f"اسم العضو الصحيح: {correct_organ}")
            await update.message.reply_text("للأسف غلطت 3 مرات. بس مش مشكلة أكتب الوصف.")
            context.user_data['organ_attempts'] = 0
            return GET_DESCRIPTION
        else:
            await update.message.reply_text("العضو غير صحيح. حاول تاني:")
            return GET_ORGAN


async def get_description(update: Update, context: CallbackContext):
    user_answer = update.message.text
    context.user_data['user_description_input'] = user_answer
    current_slide = context.user_data['current_slide']
    correct_description = current_slide['description']
    correct_organ = current_slide['organ']
    if context.user_data.get('user_organ_input') is None:
        context.user_data['user_organ_input'] = correct_organ
    answer = Answers(
        context.user_data['user_name_input'],
        user_answer,
        context.user_data['user_organ_input']
    )
    feedback_analyzer = FeedbackAnalyzer(answer)
    feedback = clean_html_generator(markdown.markdown(feedback_analyzer.analyze_answer(correct_description)))
    await update.message.reply_text(f"تقييم الإجابة:\n{feedback}",parse_mode="HTML")

    if not context.user_data['remaining_slides']:
        await update.message.reply_text("""انتهى الإختبار. شكراً لمشاركتك!
                                     لو عاوزني أطلعلك تقييم لآداءك ككل في صيغة 
                                     pdf 
                                     استخدم الأمر /SendPDF""")
        analyzer = FeedbackAnalyzer()
        formatted_feedback = get_formatted_feedback(context.user_data['feedback'])
        overall_feedback = analyzer.overall_feedback(formatted_feedback)
        context.user_data['overall_feedback'] = overall_feedback
        await update_user_rate(update, context)
        return ConversationHandler.END
    slide = context.user_data['remaining_slides'].pop(0)
    context.user_data['current_slide'] = slide
    image_path = slide['image_path']
    context.user_data['feedback'].append({'name': slide['name'], 'feedback': feedback})
    async with aiofiles.open(image_path, 'rb') as img:
        img_bytes = await img.read()
    await update.message.reply_photo(photo=img_bytes, caption="أكتب اسم هذه الشريحة:")
    return GET_NAME

async def update_user_rate(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    name_score = context.user_data.get('name_score', 0)
    organ_score = context.user_data.get('organ_score', 0)
    overall_feedback = context.user_data.get('overall_feedback', "The user did not complete the test.")
    
    users_db = Users("test.db")
    try:
        users_db.update_rate_and_feedback(user_id, name_score, organ_score, overall_feedback)
    finally:
        users_db.close()
async def development_feedback(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    now_feedback = context.user_data.get('overall_feedback', "The user did not complete the test.")
    analyzer = FeedbackAnalyzer()
    
    compared_feedback = analyzer.development_feedback(user_id, now_feedback)
    line_chart = analyzer.get_line_chart(user_id)

    try:
        users_db = Users("test.db")
        user_info = users_db.get_user_info(user_id)

        with BytesIO() as buffer:
            line_chart.savefig(buffer, format='png')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial; direction: rtl; text-align: left; }}
                    h1 {{ color: #2c3e50; }}
                    h3 {{ color: #3498db; }}
                    .score {{ background-color: #f8f9fa; padding: 10px; }}
                    hr {{ border: 0.5px solid #eee; }}
                </style>
            </head>
            <body>
                <h1>Compared feedback from the last time for {user_info}</h1>
                </br>
                <div class="score">
                    <h2>Compared feedback</h2>
                    {remove_emojis(compared_feedback)}
                </div>
                </br>
                <div class="score">
                    <h2>Line chart for development</h2>
                    <img src="data:image/png;base64,{img_base64}" alt="Line Chart">
                </div>
            </body>
            </html>
        """

        pdf_bytes = BytesIO()
        pisa.CreatePDF(html_content, dest=pdf_bytes, encoding='UTF-8')
        pdf_bytes.seek(0)

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=pdf_bytes,
            filename=f"Compared_development_for_{user_info}.pdf",
            caption="Here is your performance over time report"
        )
        
    except Exception as e:
        await update.message.reply_text(f"An error occurred while generating the PDF: {str(e)}")

    finally:
        users_db.close()

    
    

async def feedback_pdf(update: Update, context: CallbackContext):
    if 'feedback' not in context.user_data or not context.user_data['feedback']:
        await update.message.reply_text("لا يوجد تقييم متاح حتى الآن. يرجى إكمال بعض الشرائح أولاً!")
        return ConversationHandler.END
    
    try:
        users_db = Users("test.db")
        user_id = update.effective_user.id
        user_info = users_db.get_user_info(user_id)
        users_db.close()
        formatted_feedback = get_formatted_feedback(context.user_data['feedback'])
        analyzer = FeedbackAnalyzer()
        overall_feedback = analyzer.overall_feedback(formatted_feedback)
        context.user_data['overall_feedback'] = overall_feedback
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial; direction: rtl; text-align: left; }}
                h1 {{ color: #2c3e50; }}
                h3 {{ color: #3498db; }}
                .score {{ background-color: #f8f9fa; padding: 10px; }}
                hr {{ border: 0.5px solid #eee; }}
            </style>
        </head>
        <body>
            <h1>Performance report for {user_info}</h1>
            <div class="score">
                <p>Correct names: <b>{context.user_data.get('name_score', 0)}/10</b></p>
                <p>Correct organs: <b>{context.user_data.get('organ_score', 0)}/10</b></p>
            </div>
            <h2>Detailed report</h2>
            {remove_emojis(formatted_feedback)}
            <h2>Overall report</h2>
            {remove_emojis(markdown.markdown(overall_feedback))}
        </body>
        </html>
        """
        
        await update.message.reply_text("جارٍ إنشاء التقرير...")
        
        pdf_bytes = BytesIO()
        pisa.CreatePDF(html_content, dest=pdf_bytes, encoding='UTF-8')
        pdf_bytes.seek(0)
        
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=pdf_bytes,
            filename=f"Performace_report_{user_info}.pdf",
            caption="Here is your performance report"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error when handling your report {str(e)}")
        import traceback
        traceback.print_exc()
    
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, TimedOut):
        await update.message.reply_text("The request timed out. Please try again.")
    else:
        print(f"Update {update} caused error {context.error}")

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start_command)],
    states={
        GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        GET_ORGAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_organ)],
        GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
    },
    fallbacks=[CommandHandler('help', help_command),
               CommandHandler('SendPDF', feedback_pdf)],
)
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()
    app.add_handler(conversation_handler)
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('SendPDF', feedback_pdf))
    app.add_handler(CommandHandler('development', development_feedback))
    app.add_error_handler(error_handler)
    try:
        app.run_polling(poll_interval=3)
    except Exception as e:
        print(f"Error: {e}")
