import os
import json
import google.generativeai as genai

def load_settings():
    with open('setting.json', 'r') as f:
        settings = json.load(f)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings['keypass']
    credentials_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    with open(credentials_path, 'r') as file:
        credentials = json.load(file)
    return settings, credentials.get('gemini_key')

def configure_model(GEMINI_KEY, model_name):
    genai.configure(api_key=GEMINI_KEY)
    return genai.GenerativeModel(model_name)

def load_prompts():
    with open('prompt_txt2csv.txt', 'r', encoding='utf-8') as file:
        prompt_template_txt2csv = file.read()
    with open('prompt_csv2faq.txt', 'r', encoding='utf-8') as file:
        prompt_template_csv2faq = file.read()
    return prompt_template_txt2csv, prompt_template_csv2faq

def process_txt_to_csv(text_directory, csv_directory, prompt_template, model):
    txt_files = [f for f in os.listdir(text_directory) if f.endswith('.txt')]

    for txt_file in txt_files:
        txt_file_path = os.path.join(text_directory, txt_file)
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            conversation_text = file.read()
        cleaned_conversation_text = conversation_text.replace('\n', ',').replace(' ', ',')
        
        prompt = f"{prompt_template}\n\n以下が入力文です:\n{conversation_text}"
        response = model.generate_content(prompt)
        generated_content = response.text.strip()

        csv_start_index = generated_content.find("speaker,text")
        csv_content = generated_content[csv_start_index:] if csv_start_index != -1 else "speaker,text\n"

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
        
        csv_file_name = f"{os.path.splitext(txt_file)[0]}.csv"
        csv_file_path = os.path.join(csv_directory, csv_file_name)

        with open(csv_file_path, 'w', encoding='utf-8') as csv_file:
            csv_file.write(final_csv_content)

        print(f"Processed {txt_file} and saved the result to {csv_file_name}")

def process_csv_to_faq(csv_directory, faq_directory, prompt_template_csv2faq, model):
    csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]

    for csv_file_name in csv_files:
        csv_file_path = os.path.join(csv_directory, csv_file_name)
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            csv_data = csv_file.read()

        prompt_faq = f"{prompt_template_csv2faq}\n\n以下が入力文です:\n{csv_data}"
        faq_response = model.generate_content(prompt_faq)
        faq_content = faq_response.text.strip()

        faq_file_name = f"{os.path.splitext(csv_file_name)[0]}.txt"
        faq_file_path = os.path.join(faq_directory, faq_file_name)

        with open(faq_file_path, 'w', encoding='utf-8') as faq_file:
            faq_file.write(faq_content)

        print(f"Generated FAQ for {csv_file_name} and saved the result to {faq_file_name}")

if __name__ == "__main__":
    settings, GEMINI_KEY = load_settings()
    model = configure_model(GEMINI_KEY, settings['model'])
    prompt_template_txt2csv, prompt_template_csv2faq = load_prompts()

    process_txt_to_csv(settings['textfile'], settings['csvfile'], prompt_template_txt2csv, model)
    process_csv_to_faq(settings['csvfile'], settings['faqfile'], prompt_template_csv2faq, model)

    print("Finished processing all text files.")
