from django.http import HttpResponse
from django.shortcuts import render
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from django.contrib.staticfiles import finders
import os
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from deep_translator import GoogleTranslator

def animation_view(request):
	if request.method == 'POST':
		text = request.POST.get('sen')
		original_text = text
		try:
			translated = GoogleTranslator(source='auto', target='en').translate(text)
		except Exception as e:
			translated = text  
		text = translated
		text = text.lower()
		words = word_tokenize(text)

		tagged = nltk.pos_tag(words)
		tense = {}
		tense["future"] = len([word for word in tagged if word[1] == "MD"])
		tense["present"] = len([word for word in tagged if word[1] in ["VBP", "VBZ","VBG"]])
		tense["past"] = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
		tense["present_continuous"] = len([word for word in tagged if word[1] in ["VBG"]])



		stop_words = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've",'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its', "haven't", "wouldn't", 'don', 'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll", "should've", 'a', 'then', 'the', 'mustn', 'i', 'nor', 'as', "it's", "needn't", 'd', 'am', 'have',  'hasn', 'o', "aren't", "you'll", "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being', 'were', 'did', 'ma', 't', 'having', 'mightn', 've', "isn't", "won't"])



		lr = WordNetLemmatizer()
		filtered_text = []
		for w,p in zip(words,tagged):
			if w not in stop_words:
				if p[1]=='VBG' or p[1]=='VBD' or p[1]=='VBZ' or p[1]=='VBN' or p[1]=='NN':
					filtered_text.append(lr.lemmatize(w,pos='v'))
				elif p[1]=='JJ' or p[1]=='JJR' or p[1]=='JJS'or p[1]=='RBR' or p[1]=='RBS':
					filtered_text.append(lr.lemmatize(w,pos='a'))

				else:
					filtered_text.append(lr.lemmatize(w))


		words = filtered_text
		temp=[]
		for w in words:
			if w=='I':
				temp.append('Me')
			else:
				temp.append(w)
		words = temp
		probable_tense = max(tense,key=tense.get)

		if probable_tense == "past" and tense["past"]>=1:
			temp = ["Before"]
			temp = temp + words
			words = temp
		elif probable_tense == "future" and tense["future"]>=1:
			if "Will" not in words:
					temp = ["Will"]
					temp = temp + words
					words = temp
			else:
				pass
		elif probable_tense == "present":
			if tense["present_continuous"]>=1:
				temp = ["Now"]
				temp = temp + words
				words = temp


		def find_sign_images(token):
			"""Find the best single image for a token from multiple datasets"""
			token_upper = token.upper()
			
			if token.isdigit() and len(token) == 1 and '1' <= token <= '9':
				indian_folder = os.path.join(settings.BASE_DIR, 'assets', 'Indian', token)
				if os.path.exists(indian_folder):
					image_files = sorted([f for f in os.listdir(indian_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
					if image_files:
						return [f'Indian/{token}/{image_files[0]}']
			
			elif token.isalpha() and len(token) == 1:
				indian_folder = os.path.join(settings.BASE_DIR, 'assets', 'Indian', token_upper)
				if os.path.exists(indian_folder):
					image_files = sorted([f for f in os.listdir(indian_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
					if image_files:
						return [f'Indian/{token_upper}/{image_files[0]}']
			
			word_folder = os.path.join(settings.BASE_DIR, 'assets', 'ISL_CSLRT_Corpus', 'Frames_Word_Level', token_upper)
			if os.path.exists(word_folder):
				image_files = sorted([f for f in os.listdir(word_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
				if image_files:
					return [f'ISL_CSLRT_Corpus/Frames_Word_Level/{token_upper}/{image_files[0]}']
			
			char_folder = os.path.join(settings.BASE_DIR, 'assets', 'ISL_CSLRT_Corpus', 'Frames_Word_Level', token_upper)
			if os.path.exists(char_folder):
				image_files = sorted([f for f in os.listdir(char_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
				if image_files:
					return [f'ISL_CSLRT_Corpus/Frames_Word_Level/{token_upper}/{image_files[0]}']
			
			return []
		
		filtered_text = []
		word_images = {}  
		
		for w in words:
			images = find_sign_images(w)
			
			if images:
				word_images[w] = images
				filtered_text.append(w)
			else:
				word_found_as_chars = True
				for c in w:
					char_images = find_sign_images(c)
					if char_images:
						word_images[c] = char_images
						filtered_text.append(c)
					else:
						word_found_as_chars = False
						break
				
				if not word_found_as_chars:
					filtered_text.append(w)
					word_images[w] = []  
		
		words = filtered_text


		return render(request,'animation.html',{
			'words': words,
			'text': original_text,
			'translated_text': translated,
			'word_images_json': json.dumps(word_images)
		})
	else:
		return render(request,'animation.html')


@csrf_exempt
def translate_to_english(request):
	
	if request.method != 'POST':
		return JsonResponse({'error': 'POST required'}, status=405)

	try:
		data = json.loads(request.body.decode('utf-8'))
	except Exception:
		data = request.POST if request.POST else {}

	text = data.get('text') or data.get('q') or ''
	src = data.get('src') or None

	if not text:
		return JsonResponse({'error': 'No text provided'}, status=400)

	try:
		if src:
			translated = GoogleTranslator(source=src, target='en').translate(text)
		else:
			translated = GoogleTranslator(source='auto', target='en').translate(text)
		return JsonResponse({'translated': translated, 'src': src or 'auto'})
	except Exception as e:
		return JsonResponse({'error': 'Translation failed', 'detail': str(e)}, status=500)

