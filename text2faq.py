import os
import json
import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown

# Get Gemini Key
with open('setting.json', 'r') as f:
    settings = json.load(f)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings['keypass']
credentials_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
with open(credentials_path, 'r') as file:
    credentials = json.load(file)
GEMINI_KEY=credentials.get('gemini_key')
# ディレクトリの設定
text_directory = settings['textfile']
csv_directory = settings['csvfile']
model_name = settings['model']
faq_directory = settings['faqfile']
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel(model_name)

# prompt_txt2csv.txtの内容を読み込む
with open('prompt_txt2csv.txt', 'r', encoding='utf-8') as file:
    prompt_template = file.read()
# prompt_csv2faq.txtの内容を読み込む
with open('prompt_csv2faq.txt', 'r', encoding='utf-8') as file:
    prompt_template_csv2faq = file.read()

# textディレクトリ内の全てのtxtファイルを取得
txt_files = [f for f in os.listdir(text_directory) if f.endswith('.txt')]

# それぞれのtxtファイルを処理
for txt_file in txt_files:
    txt_file_path = os.path.join(text_directory, txt_file)
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        conversation_text = file.read()
    cleaned_conversation_text = conversation_text.replace('\n', ',').replace(' ', ',')
    # プロンプトの生成
    prompt = f"{prompt_template}\n\n以下が入力文です:\n{conversation_text}"

    # Gemini APIを使用してコンテンツを生成
    response = model.generate_content(prompt)
    generated_content = response.text.strip()

    # "speaker,text"以降の部分を抽出
    csv_start_index = generated_content.find("speaker,text")
    if csv_start_index != -1:
        csv_content = generated_content[csv_start_index:]
    else:
        csv_content = "speaker,text\n"  # デフォルトのヘッダー

    # CSV内容を処理して連続するスピーカーの発言をまとめる
    processed_lines = []
    last_speaker = None
    current_text = []

    for line in csv_content.splitlines():
        if line.startswith("speaker,text"):
            processed_lines.append(line)
            continue

        parts = line.split(',', 1)
        if len(parts) < 2:
            continue

        speaker, text = parts
        if speaker == last_speaker:
            current_text.append(text)
        else:
            if last_speaker is not None:
                processed_lines.append(f"{last_speaker},{' '.join(current_text)}")
            last_speaker = speaker
            current_text = [text]

    if last_speaker is not None:
        processed_lines.append(f"{last_speaker},{' '.join(current_text)}")

    final_csv_content = "\n".join(processed_lines)
    
    # 出力CSVファイルのパスを生成
    csv_file_name = f"{os.path.splitext(txt_file)[0]}.csv"
    csv_file_path = os.path.join(csv_directory, csv_file_name)

    # 結果をCSVファイルに書き込む
    with open(csv_file_path, 'w', encoding='utf-8') as csv_file:
        csv_file.write(final_csv_content)

    print(f"Processed {txt_file} and saved the result to {csv_file_name}")
    # 新たにGeminiにプロンプトを投げる
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_data = csv_file.read()

    prompt_faq = f"{prompt_template_csv2faq}\n\n以下が入力文です:\n{csv_data}"
    faq_response = model.generate_content(prompt_faq)
    faq_content = faq_response.text.strip()

    # 出力FAQファイルのパスを生成
    faq_file_name = f"{os.path.splitext(txt_file)[0]}.txt"
    faq_file_path = os.path.join(faq_directory, faq_file_name)

    # FAQコンテンツをファイルに書き込む
    with open(faq_file_path, 'w', encoding='utf-8') as faq_file:
        faq_file.write(faq_content)

    print(f"Generated FAQ for {txt_file} and saved the result to {faq_file_name}")





print("Finished processing all text files.")