import os
from PyPDF2 import PdfReader
from flask import render_template, request, flash
from flask_table import Table, Col, ButtonCol
from wtforms.validators import NoneOf
from app.llm.llm_evaluation import load_documents, prompt, prepare_llm
from app.home import bp
from config import Config
from app.home.forms import PromptForm, AddFileForm


class FileObject(object):
    def __init__(self, name) -> None:
        self.name = name


class FilesTable(Table):
    name = Col('File name')
    delete = ButtonCol('Delete?', 'home.home',
                       url_kwargs=dict(name='name'),
                       button_attrs={"name": "form_delete"})


def get_file_names():
    docs = load_documents(Config.UPLOAD_FOLDER, Config.FILE_FORMAT)
    file_names = [doc.metadata['source'].split('/')[-1] for doc in docs]
    return file_names


def convert_to_txt(document):
    reader = PdfReader(document)
    extracted_pages = [page.extract_text() for page in reader.pages]
    output_txt = " ".join(extracted_pages)
    return output_txt


@bp.route('', methods=['GET', 'POST'])
def home():
    current_file_names = get_file_names()
    add_file_form = AddFileForm(prefix="a")
    prompt_form = PromptForm(prefix="p")
    answer, duration = None, None
    for validator in add_file_form.document.validators:
        if isinstance(validator, NoneOf):
            validator.values = current_file_names
    if request.method == 'POST':
        # Handle file table
        if "form_delete" in request.values:
            os.remove(
                Config.UPLOAD_FOLDER + "/{}".format(request.args['name']))
        elif add_file_form.data['submit']:
            # Get the uploaded file
            uploaded_file = add_file_form.document.data
            # Get the filename
            filename = uploaded_file.filename
            ext = filename.split(".")[1]
            filename_without_ext = filename.split(".")[0]
            if filename in current_file_names:
                flash("File already loaded.")
            elif ext == "txt":
                uploaded_file.save(Config.UPLOAD_FOLDER + "/" + filename)
            elif ext == "pdf":
                uploaded_file_str = convert_to_txt(uploaded_file)
                with open(Config.UPLOAD_FOLDER + "/" +
                          filename_without_ext + ".txt", mode="wt") as f:
                    f.write(uploaded_file_str)
                    f.close()
        # Handle prompts
        elif prompt_form.data['submit']:
            qa_llm = prepare_llm(dir=Config.UPLOAD_FOLDER,
                                 glob=Config.FILE_FORMAT)
            answer, duration = prompt(prompt=prompt_form.prompt_text.data,
                                      qa_llm=qa_llm)
    current_file_names = get_file_names()
    file_objects = [FileObject(name=file_name)
                    for file_name in current_file_names]
    table = FilesTable(file_objects)
    table.table_id = "files"
    table.classes = ["table", "table-striped", "left-align"]

    return render_template(
        "home/home.html",
        files_available=True if current_file_names else False,
        prompt_form=prompt_form,
        answer=answer,
        duration=duration,
        table=table,
        add_file_form=add_file_form)
