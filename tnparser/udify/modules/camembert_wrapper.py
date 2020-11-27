from transformers import CamembertTokenizer

class MyCamembertTokenizer(CamembertTokenizer):

    def tokenize_to_ids_sdsadsadasd(self, text):
        if not text:
            return []
        print("TEXT:", text)
        if text == "<s>" or text == "</s>":
            pieces = [text]
        else:
            pieces = self._tokenize(text)
        print("PIECES:",pieces)
        words = []
        current_word = []
        for piece in pieces:
            if piece.startswith("\u2581"): # new word starts
                if current_word:
                    words.append(current_word)
                current_word = []
            current_word.append(piece)
        else:
            if current_word:
                words.append(current_word)
        print("WORDS:",words)
        ids = [[self._convert_token_to_id(t) for t in w] for w in words]
        
        print("IDS:", ids)

        return ids
        
        
        
        
    def tokenize_to_ids_(self, token):
        
        if not token.strip():
            print("XXXXXXXXXX empty token?", repr(token))
            return []
        token = token.strip()
        #print("TOKEN:", repr(token))
        if token == "<s>" or token == "</s>":
            pieces = [token]
        else:
            if token.startswith("\u2581"):
                pieces = self._tokenize(token[1:])
            else:
                pieces = self._tokenize(token)
                pieces[0] = pieces[0][1:] # remove "\u2581"
                if pieces[0] == "":
                    pieces = pieces[1:]
        #print("PIECES:",pieces)
        
        ids = [self._convert_token_to_id(t) for t in pieces]
        
        #print("IDS:", ids)

        return ids
