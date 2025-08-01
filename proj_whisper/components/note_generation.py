import openai
import dotenv
import os

GROUND_TRUTH_DIR = "data_dir/primock57/output/joined_transcripts" 
TRANSCRIPTIONS_DIR = "output/transcriptions"
NEW_GROUND_NOTES_DIR = "output/notes/ground"
NEW_NOTES_DIR = "output/notes/new"
dotenv.load_dotenv(dotenv.find_dotenv())

def generate_notes():
    api_key = os.getenv("open_ai_api_key")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        files = os.listdir(TRANSCRIPTIONS_DIR)
        for file in files:
            original_file = open(os.path.join(GROUND_TRUTH_DIR, file), "r")
            original_text = original_file.read()
            original_file.close()
            new_file = open(os.path.join(TRANSCRIPTIONS_DIR, file), "r")
            new_text = new_file.read()
            new_file.close()

            original_note = client.chat.completions.create(
                model = "gpt-4",
                messages=[
                    {"role": "user", "content": f"You are a medical assistant. Based on the following doctor-patient conversation transcript, create a clinical note in SOAP format. Ensure the note includes relevant details under each section (Subjective, Objective, Assessment, and Plan). Use clear, professional clinical language.\n\n TRANSCRIPT:\n {original_text}"}
                ]
            )

            new_note = client.chat.completions.create(
                model = "gpt-4",
                messages=[
                    {"role": "user", "content": f"You are a medical assistant. Based on the following doctor-patient conversation transcript, create a clinical note in SOAP format. Ensure the note includes relevant details under each section (Subjective, Objective, Assessment, and Plan). Use clear, professional clinical language.\n\n TRANSCRIPT:\n {new_text}"}
                ]
            )

            original_note_text = original_note.choices[0].message.content
            new_note_text = new_note.choices[0].message.content
            os.makedirs(NEW_GROUND_NOTES_DIR, exist_ok=True)
            os.makedirs(NEW_NOTES_DIR, exist_ok=True)
            with open(os.path.join(NEW_GROUND_NOTES_DIR, file), "w") as f:
                f.write(original_note_text)
            with open(os.path.join(NEW_NOTES_DIR, file), "w") as f:
                f.write(new_note_text)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

if __name__ == "__main__":
    generate_notes()
    print("Notes generated successfully.")
    print(f"Ground truth notes saved in {NEW_GROUND_NOTES_DIR}")