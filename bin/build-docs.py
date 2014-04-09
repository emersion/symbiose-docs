#!/usr/bin/env python

import json
import argparse

parser = argparse.ArgumentParser(description='Convert JSON docs to markdown.')
parser.add_argument('input', metavar='INPUT', type=str, help='The JSON source file.')

args = parser.parse_args()

inputPath = args.input
outputPath = '../docs/'

docs = {}

def getOutputPrefix(className):
	if isLibrary(className):
		return 'JS library_'
	if isWidget(className):
		return 'Widget_'

	return ''

def isGlobalObject(className):
	return className in ['Object', 'Function', 'Boolean', 'Error', 'Number', 'Date', 'String', 'RegExp', 'Array']

def isLibrary(className):
	return (className.find('Webos.') == 0)

def isWidget(className):
	return (className.find('$.webos.') == 0)

def isDocumented(className):
	return isLibrary(className) or isWidget(className) or isGlobalObject(className) or className in docs

def getOutputIndex(className):
	outputPrefix = getOutputPrefix(className)

	if isGlobalObject(className):
		return 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/'+className

	if isLibrary(className):
		className = className[len('Webos.'):]
	if isWidget(className):
		className = className[len('$.webos.'):]

	return outputPrefix+className.lower()

def getOutputPath(className):
	return getOutputIndex(className)+'.md'

def isPrivate(block):
	for tag in block['tags']:
		if tag['type'] == 'private':
			return True

	return False

def formatSince(tags):
	since = ''
	for tag in tags:
		if tag['type'] == 'since':
			since = tag['string']
			return '\n\nSince ['+since+'](../releases/tag/'+since+').'

	return ''

def formatAugments(tags):
	augments = ''
	for tag in tags:
		if tag['type'] == 'augments':
			augments = tag['otherClass']
			return '\n\nChild of '+formatTypes(augments)+'.'

	return ''

def formatInlineDeprecated(tags):
	deprecated = ''
	for tag in tags:
		if tag['type'] == 'deprecated':
			deprecated = tag['string']
			return '**Deprecated**: '+deprecated+'.'

	return ''

def formatDeprecated(tags):
	deprecated = formatInlineDeprecated(tags)

	if len(deprecated) > 0:
		return '\n\n'+deprecated
	else:
		return ''

def formatTypes(types):
	if type(types) == str:
		types = [types]
	
	i = 0
	for typeName in types:
		if typeName[0] == '{' and typeName[-1] == '}':
			typeName = typeName[1:-1]

		if isDocumented(typeName):
			types[i] = '['+typeName+']('+getOutputIndex(typeName)+')'
		else:
			types[i] = typeName
		i += 1
		
	return '_'+'|'.join(types)+'_'

def formatReturnTypes(tags):
	for tag in tags:
		if tag['type'] == 'return' or tag['type'] == 'returns':
			if 'types' in tag:
				return formatTypes(tag['types'])+' '
	return ''

def formatParamsList(tags):
	paramsList = []
	for tag in tags:
		if tag['type'] == 'param':
			if 'types' in tag:
				#paramTypes = formatTypes(tag['types']) #Do not print param types in params list
				paramTypes = ''
			else:
				paramTypes = ''
			paramsList.append(paramTypes+'**'+tag['name']+'**')
	return ', '.join(paramsList)

def formatParamsDescription(tags):
	paramsDescription = []
	for tag in tags:
		if tag['type'] == 'param':
			if 'types' in tag:
				paramTypes = formatTypes(tag['types'])+' '
			else:
				paramTypes = ''
			paramsDescription.append(paramTypes+'**'+tag['name']+'** '+tag['description'])
	if len(paramsDescription) == 0:
		return ''
	else:
		return '\n * ' + '\n * '.join(paramsDescription)

try:
	data = json.load(open(inputPath,'r'))
except ValueError:
	data = []

# Order by type
fileOverview = None
i = 0
for block in data:
	if 'ctx' in block:
		ctx = block['ctx']

		# Is it a class ?
		if ctx['type'] == 'constructor':
			if 'receiver' in ctx:
				className = ctx['receiver'] + '.' + ctx['name']
			else:
				className = ctx['name']

			if className in docs:
				docs[className]['class'] = block
			else:
				docs[className] = {
					'class': block,
					'static_method': [],
					'method': [],
					'property':[],
					'static_property':[],
					'prototype':[]
				}
			continue

		parent = None
		static = True
		if 'constructor' in ctx:
			parent = ctx['constructor']
			static = False
		elif 'receiver' in ctx:
			parent = ctx['receiver']

		if parent is None:
			continue

		if isPrivate(block):
			continue
		
		blockType = ctx['type']
		if static and blockType != 'prototype':
			blockType = 'static_'+blockType

		if parent not in docs:
			docs[parent] = {
				'class': None,
				'static_method': [],
				'method': [],
				'property':[],
				'static_property':[],
				'prototype':[]
			}
		docs[parent][blockType].append(block)
	else:
		if i == 0: # First tag & without ctx, maybe a file overview
			fileOverview = block
	i += 1


# For each class
for className in docs.keys():
	classDoc = docs[className]

	if className == 'this':
		continue

	output = ''

	# Class
	if 'class' in classDoc and classDoc['class'] is not None:
		output += classDoc['class']['description']['full']
		output += formatSince(classDoc['class']['tags'])
		output += formatAugments(classDoc['class']['tags'])
		output += formatDeprecated(classDoc['class']['tags'])
		output += '\n\n'

	# Options
	if isWidget(className):
		output += '# Options\n\n'

		options = None
		for block in classDoc['property']:
			ctx = block['ctx']
			if ctx['name'] == 'options':
				options = block
				break

		if options is not None:
			output += block['description']['full']+'\n'
		else:
			output += '_This widget hasn\'t any option._\n'

		output += '\n'
	else:
		pass #TODO: print properties

	# Methods
	output += '# Methods\n\n'
	for block in classDoc['method']:
		ctx = block['ctx']

		methodName = '**'+ctx['name']+'**'

		returnTypes = formatReturnTypes(block['tags'])
		paramsList = formatParamsList(block['tags'])
		paramsDescription = formatParamsDescription(block['tags'])
		deprecated = formatInlineDeprecated(block['tags'])
		summary = block['description']['summary'].strip()

		output += '* '+returnTypes+methodName+'('+paramsList+') : '+summary

		if len(deprecated) > 0:
			output += '\n  '+deprecated
		if len(paramsDescription) > 0:
			output += paramsDescription

		output += '\n'

	if len(classDoc['method']) == 0:
		output += '_This class hasn\'t any method._\n'

	output += '\n'

	# Static methods
	output += '# Static methods\n\n'
	for block in classDoc['static_method']:
		ctx = block['ctx']

		methodName = ctx['receiver'] + '.**'+ctx['name']+'**'

		returnTypes = formatReturnTypes(block['tags'])
		paramsList = formatParamsList(block['tags'])
		paramsDescription = formatParamsDescription(block['tags'])
		deprecated = formatInlineDeprecated(block['tags'])
		summary = block['description']['summary'].strip()

		output += '* '+returnTypes+methodName+'('+paramsList+') : '+summary

		if len(deprecated) > 0:
			output += '\n  '+deprecated
		if len(paramsDescription) > 0:
			output += paramsDescription

		output += '\n'

	if len(classDoc['static_method']) == 0:
		output += '_This class hasn\'t any static method._\n'

	outputFile = open(outputPath+'/'+getOutputPath(className), 'w')
	outputFile.write(output)