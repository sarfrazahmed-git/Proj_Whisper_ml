import os
import spacy

ORIGINAL_NOTES_DIR = "output/notes/ground"
NEW_NOTES_DIR = "output/notes/new"
# Load SciSpacy model (detects diseases & chemicals)
nlp = spacy.load("en_ner_bc5cdr_md")

def get_matches(text):
    """
    Extract entities using SpaCy model (no UMLS).
    Returns a dict of terms and a flat list of terms.
    """
    concepts = {}
    term_list = []

    doc = nlp(text)
    for ent in doc.ents:
        key = (ent.text.lower(), ent.label_)  # example: ("diabetes", "DISEASE")
        if ent.text not in concepts.get(key, []):
            concepts[key] = concepts.get(key, []) + [ent.text]
            term_list.append(ent.text.lower())

    return concepts, term_list

def umls_score_individual(reference, prediction):

    true_concept, true_terms = get_matches(reference)
    pred_concept, pred_terms = get_matches(prediction)

    try:
        num_matched = 0
        for key in true_concept:
            # If any of the reference terms appear in predicted terms
            if any(term.lower() in [pt.lower() for pt in pred_terms] for term in true_concept[key]):
                num_matched += 1

        precision = num_matched / len(pred_concept) if pred_concept else 0
        recall = num_matched / len(true_concept) if true_concept else 0

        if precision + recall == 0:
            return 0

        f1 = 2 * (precision * recall) / (precision + recall)
        return f1
    except:
        return 0

def umls_score_group(references, predictions):   
    return [
        umls_score_individual(reference, prediction)
        for reference, prediction in zip(references, predictions)
    ]



if __name__ == "__main__":
    files = os.listdir(ORIGINAL_NOTES_DIR)

    for file in files:
        original_file = open(os.path.join(ORIGINAL_NOTES_DIR, file), "r")
        original_text = original_file.read()
        original_file.close()

        new_file = open(os.path.join(NEW_NOTES_DIR, file), "r")
        new_text = new_file.read()
        new_file.close()

        score = umls_score_individual(original_text, new_text)
        print(f"UMLS Score for {file}: {score:.4f}")