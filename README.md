# FAQmaker

# 初期設定
## 実行ファイルのセットアップ
1. soundの中に変換したい音声ファイルが含まれていることを確認してください
2. 以下を実行してください
```
    .\run_scripts.bat
```

## 環境設定
SDKの設定は略
IAMからユーザーにロールとして
[その他]>[Cloud Speechクライアント]
[Cloud Storage]>[Storageオブジェクト管理者]
を追加してください

細かい設定は大体`setting.json`で弄れます
またタイムアウトの時間は20分を設定していますがあまりにも長い動画で動かしたいなら適当に変えてください
Cloud Storageに`pushstorage`を追加してください
StorageはSTTのために利用するだけなのでライフサイクルで自動的に消すようにした方がいいかも

環境変数はenvi下に置いてるjsonを参照
サービスアカウントから鍵を追加し，ここに指定された場所においてください
また、キーにGeminiから取ってきたキーを`Gemini_key`として追加してください
```
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\envi\\credentials-file.json'
    credentials_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    with open(credentials_path, 'r') as file:
        credentials = json.load(file)
    project_id = credentials.get('project_id')
```

# ファイル

## sound
音声ファイル一覧
ここに保存された音声を全てFAQに変換します
mp3以外は対応してないためwavとか使いたいなら書き換えてください

## reco2text.py
Cloud Storageに送信し，音声変換を行います
変換されたテキストは`text`フォルダに格納されます
## text2faq
csvフォルダ下にやり取りを分割したものを
faqフォルダ下にcsvから作成したfaqを載せています

