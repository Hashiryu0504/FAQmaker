import os

def merge_text_files(input_folder, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(input_folder):
            if filename.endswith('.txt'):
                with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    outfile.write("\n\n")  # ファイル間にスペースを追加するため
    print(f"All text files have been merged into {output_file}")

# 使用例
input_folder = 'faq'
output_file = 'merged_faq.txt'
merge_text_files(input_folder, output_file)
