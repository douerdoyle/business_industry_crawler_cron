import re

#移除文章中的html註解
regex_comment = r'<!--[\W\w\d]+-->'

def get_tag_text(tag):
	text = ""
	try:
		text = tag.get_text().strip().replace("\n","")
		comments = re.findall(regex_comment, text)
		for comment in comments:
			text = text.replace(comment,"")
	except Exception as e:
		text = tag.strip().replace("\n","")
	return text

def get_tag_attr(tag, attr):
	attr_value = ""
	try:
		attr_value = tag[attr]
	except Exception as e:
		attr_value=None
	return attr_value