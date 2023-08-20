from flask import render_template, request
from app.llm.llm_evaluation import prompt
from app.llm.llm_evaluation import prepare_llm
from app.home import bp
from config import Config
from app.home.forms import PromptForm


@bp.route('', methods=['GET', 'POST', 'PUT'])
def home():
    answer = None
    prompt_form = PromptForm()
    qa_llm = prepare_llm(dir=Config.UPLOAD_FOLDER,
                         glob=Config.FILE_FORMAT)
    if request.method == "POST":
        answer = prompt(prompt=prompt_form.prompt_text.data,
                        qa_llm=qa_llm)
    return render_template("home/home.html",
                           files_available=True if qa_llm else False,
                           prompt_form=prompt_form,
                           answer=answer)
