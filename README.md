# lifoid-chatui

Chatbot UI provides a Web messaging app for chatbots built with Lifoid.

The Web App is delivered as a Python Flask blueprint for Lifoid.

## Installation

```
pip install lifoid-chatui
```

## Configuration

lifoid-chatui requires two specific environment variables:
- ``PATH_URL``: Lifoid chatbot endpoint
- ``COMPANY_NAME``: Name of company to display in terms of service and privacy pages

lifoid-chatui also uses environment variables from Lifoid configuration:
- ``LIFOID_NAME``: Name of service displayed as a Logo
- ``COGNITO_AUTH``: if ``yes`` then Amazon AWS Cognito login and signup pages are integrated. Then we need ``COGNITO_CLIENTID``, ``COGNITO_APPWEBDOMAIN``, ``COGNITO_CERTIFICATE_URL``, ``COGNITO_REDIRECTURISIGNIN``, and ``COGNITO_REDIRECTURISIGNOUT``
- ``GOOGLE_APPLICATION_CREDENTIALS``: used to access Google Speech Cloud API
- ``AWS_DEFAULT_REGION``: used to access Amazon AWS Polly API. Not required if Lifoid is running on an Amazon AWS environment such as Lambda or EC2
- ``SPEECH_VOICE``: Default voice name from Amazon AWS Polly (Matthew)
- ``LANG_RECO``: Default language for speech recognition on Google Speech (en-us)

## Development

**Chatbot localization**

Initialization

```bash
$ pybabel -v extract -F babel.cfg -o ./lifoid_chatui/translations/messages.pot ./
$ pybabel init -i ./lifoid_chatui/translations/messages.pot -d ./lifoid_chatui/translations -l ja
```

Update

```bash
$ pybabel -v extract -F babel.cfg -o ./lifoid_chatui/translations/messages.pot ./
$ pybabel update -i ./lifoid_chatui/translations/messages.pot -d ./bot/translations
```

Compile

```bash
$ pybabel compile -d ./lifoid_chatui/translations/
```

**JS minify**

```bash
uglifyjs ./lifoid_chatui/static/assets/plugins/lifoid/jquery-lifoid-chat.js -c -m -v -o ./lifoid_chatui/static/assets/plugins/lifoid/jquery-lifoid-chat.min.js
```

## Speech interface

### List of languages for Google Speech Cloud

Afrikaans (Suid-Afrika) 	af-ZA 	Afrikaans (South Africa)
አማርኛ (ኢትዮጵያ) 	am-ET 	Amharic (Ethiopia)
Հայ (Հայաստան) 	hy-AM 	Armenian (Armenia)
Azərbaycan (Azərbaycan) 	az-AZ 	Azerbaijani (Azerbaijan)
Bahasa Indonesia (Indonesia) 	id-ID 	Indonesian (Indonesia)
Bahasa Melayu (Malaysia) 	ms-MY 	Malay (Malaysia)
বাংলা (বাংলাদেশ) 	bn-BD 	Bengali (Bangladesh)
বাংলা (ভারত) 	bn-IN 	Bengali (India)
Català (Espanya) 	ca-ES 	Catalan (Spain)
Čeština (Česká republika) 	cs-CZ 	Czech (Czech Republic)
Dansk (Danmark) 	da-DK 	Danish (Denmark)
Deutsch (Deutschland) 	de-DE 	German (Germany)
English (Australia) 	en-AU 	English (Australia)
English (Canada) 	en-CA 	English (Canada)
English (Ghana) 	en-GH 	English (Ghana)
English (Great Britain) 	en-GB 	English (United Kingdom)
English (India) 	en-IN 	English (India)
English (Ireland) 	en-IE 	English (Ireland)
English (Kenya) 	en-KE 	English (Kenya)
English (New Zealand) 	en-NZ 	English (New Zealand)
English (Nigeria) 	en-NG 	English (Nigeria)
English (Philippines) 	en-PH 	English (Philippines)
English (South Africa) 	en-ZA 	English (South Africa)
English (Tanzania) 	en-TZ 	English (Tanzania)
English (United States) 	en-US 	English (United States)
Español (Argentina) 	es-AR 	Spanish (Argentina)
Español (Bolivia) 	es-BO 	Spanish (Bolivia)
Español (Chile) 	es-CL 	Spanish (Chile)
Español (Colombia) 	es-CO 	Spanish (Colombia)
Español (Costa Rica) 	es-CR 	Spanish (Costa Rica)
Español (Ecuador) 	es-EC 	Spanish (Ecuador)
Español (El Salvador) 	es-SV 	Spanish (El Salvador)
Español (España) 	es-ES 	Spanish (Spain)
Español (Estados Unidos) 	es-US 	Spanish (United States)
Español (Guatemala) 	es-GT 	Spanish (Guatemala)
Español (Honduras) 	es-HN 	Spanish (Honduras)
Español (México) 	es-MX 	Spanish (Mexico)
Español (Nicaragua) 	es-NI 	Spanish (Nicaragua)
Español (Panamá) 	es-PA 	Spanish (Panama)
Español (Paraguay) 	es-PY 	Spanish (Paraguay)
Español (Perú) 	es-PE 	Spanish (Peru)
Español (Puerto Rico) 	es-PR 	Spanish (Puerto Rico)
Español (República Dominicana) 	es-DO 	Spanish (Dominican Republic)
Español (Uruguay) 	es-UY 	Spanish (Uruguay)
Español (Venezuela) 	es-VE 	Spanish (Venezuela)
Euskara (Espainia) 	eu-ES 	Basque (Spain)
Filipino (Pilipinas) 	fil-PH 	Filipino (Philippines)
Français (Canada) 	fr-CA 	French (Canada)
Français (France) 	fr-FR 	French (France)
Galego (España) 	gl-ES 	Galician (Spain)
ქართული (საქართველო) 	ka-GE 	Georgian (Georgia)
ગુજરાતી (ભારત) 	gu-IN 	Gujarati (India)
Hrvatski (Hrvatska) 	hr-HR 	Croatian (Croatia)
IsiZulu (Ningizimu Afrika) 	zu-ZA 	Zulu (South Africa)
Íslenska (Ísland) 	is-IS 	Icelandic (Iceland)
Italiano (Italia) 	it-IT 	Italian (Italy)
Jawa (Indonesia) 	jv-ID 	Javanese (Indonesia)
ಕನ್ನಡ (ಭಾರತ) 	kn-IN 	Kannada (India)
ភាសាខ្មែរ (កម្ពុជា) 	km-KH 	Khmer (Cambodia)
ລາວ (ລາວ) 	lo-LA 	Lao (Laos)
Latviešu (latviešu) 	lv-LV 	Latvian (Latvia)
Lietuvių (Lietuva) 	lt-LT 	Lithuanian (Lithuania)
Magyar (Magyarország) 	hu-HU 	Hungarian (Hungary)
മലയാളം (ഇന്ത്യ) 	ml-IN 	Malayalam (India)
मराठी (भारत) 	mr-IN 	Marathi (India)
Nederlands (Nederland) 	nl-NL 	Dutch (Netherlands)
नेपाली (नेपाल) 	ne-NP 	Nepali (Nepal)
Norsk bokmål (Norge) 	nb-NO 	Norwegian Bokmål (Norway)
Polski (Polska) 	pl-PL 	Polish (Poland)
Português (Brasil) 	pt-BR 	Portuguese (Brazil)
Português (Portugal) 	pt-PT 	Portuguese (Portugal)
Română (România) 	ro-RO 	Romanian (Romania)
සිංහල (ශ්රී ලංකාව) 	si-LK 	Sinhala (Sri Lanka)
Slovenčina (Slovensko) 	sk-SK 	Slovak (Slovakia)
Slovenščina (Slovenija) 	sl-SI 	Slovenian (Slovenia)
Urang (Indonesia) 	su-ID 	Sundanese (Indonesia)
Swahili (Tanzania) 	sw-TZ 	Swahili (Tanzania)
Swahili (Kenya) 	sw-KE 	Swahili (Kenya)
Suomi (Suomi) 	fi-FI 	Finnish (Finland)
Svenska (Sverige) 	sv-SE 	Swedish (Sweden)
தமிழ் (இந்தியா) 	ta-IN 	Tamil (India)
தமிழ் (சிங்கப்பூர்) 	ta-SG 	Tamil (Singapore)
தமிழ் (இலங்கை) 	ta-LK 	Tamil (Sri Lanka)
தமிழ் (மலேசியா) 	ta-MY 	Tamil (Malaysia)
తెలుగు (భారతదేశం) 	te-IN 	Telugu (India)
Tiếng Việt (Việt Nam) 	vi-VN 	Vietnamese (Vietnam)
Türkçe (Türkiye) 	tr-TR 	Turkish (Turkey)
اردو (پاکستان) 	ur-PK 	Urdu (Pakistan)
اردو (بھارت) 	ur-IN 	Urdu (India)
Ελληνικά (Ελλάδα) 	el-GR 	Greek (Greece)
Български (България) 	bg-BG 	Bulgarian (Bulgaria)
Русский (Россия) 	ru-RU 	Russian (Russia)
Српски (Србија) 	sr-RS 	Serbian (Serbia)
Українська (Україна) 	uk-UA 	Ukrainian (Ukraine)
עברית (ישראל) 	he-IL 	Hebrew (Israel)
العربية (إسرائيل) 	ar-IL 	Arabic (Israel)
العربية (الأردن) 	ar-JO 	Arabic (Jordan)
العربية (الإمارات) 	ar-AE 	Arabic (United Arab Emirates)
العربية (البحرين) 	ar-BH 	Arabic (Bahrain)
العربية (الجزائر) 	ar-DZ 	Arabic (Algeria)
العربية (السعودية) 	ar-SA 	Arabic (Saudi Arabia)
العربية (العراق) 	ar-IQ 	Arabic (Iraq)
العربية (الكويت) 	ar-KW 	Arabic (Kuwait)
العربية (المغرب) 	ar-MA 	Arabic (Morocco)
العربية (تونس) 	ar-TN 	Arabic (Tunisia)
العربية (عُمان) 	ar-OM 	Arabic (Oman)
العربية (فلسطين) 	ar-PS 	Arabic (State of Palestine)
العربية (قطر) 	ar-QA 	Arabic (Qatar)
العربية (لبنان) 	ar-LB 	Arabic (Lebanon)
العربية (مصر) 	ar-EG 	Arabic (Egypt)
فارسی (ایران) 	fa-IR 	Persian (Iran)
हिन्दी (भारत) 	hi-IN 	Hindi (India)
ไทย (ประเทศไทย) 	th-TH 	Thai (Thailand)
한국어 (대한민국) 	ko-KR 	Korean (South Korea)
國語 (台灣) 	cmn-Hant-TW 	Chinese, Mandarin (Traditional, Taiwan)
廣東話 (香港) 	yue-Hant-HK 	Chinese, Cantonese (Traditional, Hong Kong)
日本語（日本） 	ja-JP 	Japanese (Japan)
普通話 (香港) 	cmn-Hans-HK 	Chinese, Mandarin (Simplified, Hong Kong)
普通话 (中国大陆) 	cmn-Hans-CN 	Chinese, Mandarin (Simplified, China)

### List of voices for Amazon Polly

 Ivy  --> Ivy [English - American] 
 Joanna  --> Joanna [English - American] 
 Joey  --> Joey [English - American] 
 Justin  --> Justin [English - American] 
 Kendra  --> Kendra [English - American]  
 Kimberly  --> Kimberly [English - American] 
 Salli  --> Salli [English - American] 
 Nicole  --> Nicole [English - Australian] 
 Russell  --> Russell [English - Australian] 
 Emma  --> Emma [English - British] 
 Brian  --> Brian [English - British] 
 Amy  --> Amy [English - British] 
 Raveena  --> Raveena [English - Indian]         
 Geraint  --> Geraint [English - Welsh] 
 Ricardo  --> Ricardo [Brazilian Portuguese] 
 Vitória  --> Vitória [Brazilian Portuguese] 
 Lotte  --> Lotte [Dutch] 
 Ruben  --> Ruben [Dutch] 
 Mathieu  --> Mathieu [French] 
 Céline  --> Céline [French] 
 Chantal  --> Chantal [Canadian French] 
 Marlene  --> Marlene [German] 
 Dóra  --> Dóra [Icelandic] 
 Karl  --> Karl [Icelandic] 
 Carla  --> Carla [Italian] 
 Giorgio  --> Giorgio [Italian] 
 Mizuki  --> Mizuki [Japanese] 
 Liv  --> Liv [Norwegian] 
 Maja  --> Maja [Polish] 
 Jan  --> Jan [Polish] 
 Ewa  --> Ewa [Polish] 
 Cristiano  --> Cristiano [Portuquese] 
 Inês  --> Inês [Portuquese] 
 Carmen  --> Carmen [Romanian] 
 Maxim  --> Maxim [Russian] 
 Tatyana  --> Tatyana [Russian] 
 Enrique  --> Enrique [Spanish] 
 Penélope  --> Penélope [US Spanish] 
 Enrique  --> Miguel [US Spanish] 
 Conchita  --> Conchita [Castilian Spanish] 
 Astrid  --> Astrid [Swedish] 
 Filiz  --> Filiz [Turkish] 
 Gwyneth  --> Gwyneth [Welsh] 


