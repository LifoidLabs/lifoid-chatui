# lifoid-chatui

Chat UI plugin for Lifoid. It provides a native Web messaging app to have a 
one to one conversation with a chatbot.

## Installation

```
pip install lifoid-chatui
```

#" Development

**Chatbot localization**

Initialization

```bash
$ pybabel -v extract -F babel.cfg -o ./lifoid_chatui/translations/messages.pot ./
$ pybabel init -i ./lifoid_chatui/translations/messages.pot -d ./lifoid_chatui/translations -l ja
```

Update

```bash
$ pybabel -v extract -F babel.cfg -o ./lifoid/www/translations/messages.pot ./
$ pybabel update -i ./lifoid/www/translations/messages.pot -d ./bot/translations
```

Compile

```bash
$ pybabel compile -d ./lifoid/www/translations/
```

**JS minify**

```bash
uglifyjs ./lifoid_chatui/static/assets/plugins/lifoid/jquery-lifoid-chat.js -c -m -v -o ./lifoid_chatui/static/assets/plugins/lifoid/jquery-lifoid-chat.min.js
```

