import os
import json
from google.cloud import storage
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech


# setting.jsonから初期設定の読み込み
with open('setting.json', 'r') as f:
    settings = json.load(f)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings['keypass']
timeout = settings['timeout']
retries = settings['retries']
text_directory = settings['textfile']

bucket_name = settings['storage']
sound_directory = settings['recofile']
# プロジェクトID所得
credentials_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
with open(credentials_path, 'r') as file:
    credentials = json.load(file)

project_id = credentials.get('project_id')

###########################
###########################
###########################

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """GCSにファイルをアップロードする"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    if blob.exists():
        print(f"File {destination_blob_name} already exists in the bucket. Skipping upload.")
        return

    for attempt in range(retries):
        try:
            blob.upload_from_filename(source_file_name, timeout=timeout)  # タイムアウトを設定
            print(f"File {source_file_name} uploaded to {destination_blob_name}.")
            return
        except Exception as e:
            print(f"Upload failed: {e}. Retrying {attempt + 1}/{retries}...")
            if attempt == retries - 1:
                raise e

def transcribe_batch_gcs_input_inline_output_v2(
    project_id: str,
    gcs_uri: str,
# ) -> cloud_speech.BatchRecognizeResults:
) -> str:
    """Transcribes audio from a Google Cloud Storage URI.

    Args:
        project_id: The Google Cloud project ID.
        gcs_uri: The Google Cloud Storage URI.

    Returns:
        The RecognizeResponse.
    """
    # Instantiates a client
    client = SpeechClient()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["ja-JP"],
        model="telephony",
    )

    file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=gcs_uri)

    request = cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{project_id}/locations/global/recognizers/_",
        config=config,
        files=[file_metadata],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            inline_response_config=cloud_speech.InlineOutputConfig(),
        ),
    )

    # Transcribes the audio into text
    operation = client.batch_recognize(request=request)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=timeout)

    # Check if there are results and handle them appropriately
    transcript = ""
    if gcs_uri in response.results:
        for result in response.results[gcs_uri].transcript.results:
            if result.alternatives:
                transcript += f"{result.alternatives[0].transcript}\n"
                print(f"{result.alternatives[0].transcript}")
            else:
                print("No alternatives found for this result.")
    else:
        print("No results found for the specified GCS URI.")

    return transcript
    # return response.results.get(gcs_uri).transcript if gcs_uri in response.results else None


def reco2text():
    # soundディレクトリ内の全てのmp3ファイルを取得
    mp3_files = [f for f in os.listdir(sound_directory) if f.endswith('.mp3')]
    total_files = len(mp3_files)
    # それぞれのmp3ファイルをアップロード
    for idx, mp3_file in enumerate(mp3_files, start=1):
        print(f"Uploading file {idx} of {total_files}...")
        source_file_name = os.path.join(sound_directory, mp3_file)
        destination_blob_name = mp3_file
        upload_to_gcs(bucket_name, source_file_name, destination_blob_name)
        # 文字起こし
        gcs_uri = 'gs://'+bucket_name+'/'+mp3_file 
        transcript = transcribe_batch_gcs_input_inline_output_v2(project_id, gcs_uri)
        text_file_name = os.path.join(text_directory, f"{os.path.splitext(mp3_file)[0]}.txt")
        with open(text_file_name, 'w', encoding='utf-8') as text_file:
            text_file.write(transcript)
    print(f"finish all recoss")

if __name__=='__main__':
    reco2text()