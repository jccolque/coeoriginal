#Imports Python
import hashlib
#Imports Django
#Import Personales

def TokenGenerator(individuo):
    text = str(individuo.pk) + individuo.num_doc
    return hashlib.sha224(text.encode()).hexdigest()